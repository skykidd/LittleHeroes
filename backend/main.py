from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
from openai import OpenAI
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor
from io import BytesIO

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load knowledge base
def load_knowledge_base():
    # Try multiple possible paths
    possible_paths = [
        './knowledge_base',
        '../knowledge_base',
        'knowledge_base',
        os.path.join(os.path.dirname(__file__), 'knowledge_base'),
        os.path.join(os.path.dirname(__file__), '..', 'knowledge_base')
    ]
    
    for kb_path in possible_paths:
        if os.path.exists(kb_path):
            print(f"📁 Found knowledge base at: {kb_path}")
            try:
                loader = DirectoryLoader(
                    kb_path,
                    glob="**/*.md",
                    loader_cls=TextLoader,
                    loader_kwargs={'encoding': 'utf-8'}
                )
                documents = loader.load()
                
                if not documents:
                    print(f"⚠️ Warning: No markdown files found in {kb_path}")
                    continue
                
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                texts = text_splitter.split_documents(documents)
                
                encode_kwargs = {'normalize_embeddings': False}
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    encode_kwargs=encode_kwargs
                )
                
                vectorstore = FAISS.from_documents(texts, embeddings)
                print(f"✅ Loaded {len(documents)} documents from knowledge base!")
                return vectorstore
            except Exception as e:
                print(f"⚠️ Error loading from {kb_path}: {e}")
                continue
    
    print("⚠️ Warning: Could not find knowledge base in any expected location")
    return None

vectorstore = load_knowledge_base()

class StoryRequest(BaseModel):
    child_name: str
    age: int
    condition: str  
    treatment: str
    interests: str
    output_type: str = "text"  # "text" or "storybook"

def retrieve_medical_context(condition: str, treatment: str, age: int):
    if not vectorstore:
        return "Medical context unavailable."
        
    query = f"{condition} {treatment} for {age} year old child"
    docs = vectorstore.similarity_search(query, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])
    return context

def safety_check(content: str) -> bool:
    unsafe_terms = ["scary", "painful", "dangerous", "death", "die"]
    return not any(term in content.lower() for term in unsafe_terms)

def generate_storybook_content(story: str, child_name: str, interests: str, age: int):
    """Break story into pages with illustration prompts"""
    prompt = f"""Break this story into exactly 4 storybook pages. For each page:
- Provide the text (2-3 sentences max per page)
- Create a detailed illustration prompt for a 2D flat-style children's book image

Story: {story}

Format each page as:
PAGE X:
TEXT: [page text]
ILLUSTRATION: [detailed prompt for 2D flat illustration featuring {child_name}, age {age}, in a simple, colorful, flat cartoon style with minimal shadows and clean shapes]

Create exactly 4 pages now:"""

    message = anthropic_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    content = message.content[0].text
    
    # Parse pages
    pages = []
    current_page = {}
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('PAGE'):
            if current_page:
                pages.append(current_page)
            current_page = {'page_num': line}
        elif line.startswith('TEXT:'):
            current_page['text'] = line.replace('TEXT:', '').strip()
        elif line.startswith('ILLUSTRATION:'):
            current_page['illustration_prompt'] = line.replace('ILLUSTRATION:', '').strip()
    
    if current_page:
        pages.append(current_page)
    
    # Limit to 4 pages max
    return pages[:4]

def generate_illustration_dalle(prompt: str, page_num: int):
    """Generate illustration using DALL-E 3"""
    if not openai_client.api_key:
        print(f"⚠️ No OpenAI API key, using placeholder for page {page_num}")
        return None
    
    print(f"🎨 Generating illustration {page_num} with DALL-E 3...")
    
    # Enhanced prompt for 2D flat illustration style
    full_prompt = f"{prompt}, 2D flat illustration, simple flat design, children's book art, colorful and friendly cartoon style, flat vector art, minimal shadows, bright colors, clean shapes, 2D design, flat style storybook illustration, whimsical 2D art, appropriate for children"
    
    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1024x1024",  # DALL-E 3 sizes: 1024x1024, 1792x1024, 1024x1792
            quality="standard",  # "standard" or "hd"
            n=1,
        )
        
        image_url = response.data[0].url
        
        # Download image
        img_response = requests.get(image_url)
        
        if img_response.status_code == 200:
            print(f"✅ Illustration {page_num} generated")
            return BytesIO(img_response.content)
        else:
            print(f"❌ Failed to download illustration {page_num}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating illustration {page_num}: {e}")
        return None

def create_pdf_storybook(pages, child_name: str, condition: str):
    """Create beautiful PDF storybook"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=HexColor('#4682b4'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    text_style = ParagraphStyle(
        'StoryText',
        parent=styles['BodyText'],
        fontSize=14,
        leading=20,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        fontName='Helvetica'
    )
    
    story_elements = []
    
    # Cover page
    story_elements.append(Spacer(1, 1*inch))
    story_elements.append(Paragraph(f"{child_name}'s Special Story", title_style))
    story_elements.append(Spacer(1, 0.3*inch))
    story_elements.append(Paragraph(
        f"A brave journey through {condition}",
        ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=16, alignment=TA_CENTER, textColor=HexColor('#666666'))
    ))
    story_elements.append(PageBreak())
    
    # Story pages
    for i, page in enumerate(pages, 1):
        # Add illustration if available
        if page.get('image'):
            try:
                img = Image(page['image'], width=5*inch, height=5*inch)
                img.hAlign = 'CENTER'
                story_elements.append(Spacer(1, 0.5*inch))
                story_elements.append(img)
                story_elements.append(Spacer(1, 0.3*inch))
            except Exception as e:
                print(f"⚠️ Could not add image for page {i}: {e}")
        
        # Add text
        if page.get('text'):
            story_elements.append(Paragraph(page['text'], text_style))
        
        # Page break except for last page
        if i < len(pages):
            story_elements.append(PageBreak())
    
    # Build PDF
    doc.build(story_elements)
    buffer.seek(0)
    return buffer

@app.post("/generate-story")
async def generate_story(request: StoryRequest):
    try:
        print(f"\n{'='*50}")
        print(f"📝 Generating story for {request.child_name}")
        print(f"   Age: {request.age}, Condition: {request.condition}")
        print(f"   Output: {request.output_type}")
        print(f"{'='*50}\n")
        
        # 1. Retrieve medical context
        medical_context = retrieve_medical_context(
            request.condition,
            request.treatment,
            request.age
        )
        
        # 2. Generate story
        prompt = f"""Using this medical information:

{medical_context}

Create a comforting, age-appropriate story for a {request.age}-year-old child named {request.child_name} who has {request.condition} and is undergoing {request.treatment}.

The child enjoys {request.interests}.

Story Requirements:
- Positive and empowering tone
- Scientifically accurate but simple explanations
- Feature {request.child_name} as the brave hero
- Include elements related to their interests: {request.interests}
- Explain the treatment as a helpful journey
- Use age-appropriate language for a {request.age}-year-old
- 5-7 paragraphs for storybook format
- Avoid scary or painful descriptions

Story:"""

        message = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        story = message.content[0].text
        print(f"✅ Story generated ({len(story)} characters)")
        
        # 3. Safety check
        if not safety_check(story):
            raise HTTPException(
                status_code=400,
                detail="Generated story failed safety checks"
            )
        
        # 4. Generate storybook if requested
        pdf_data = None
        if request.output_type == "storybook":
            try:
                print("📚 Creating storybook pages...")
                pages = generate_storybook_content(
                    story,
                    request.child_name,
                    request.interests,
                    request.age
                )
                
                print(f"✅ Created {len(pages)} pages")
                
                # Generate illustrations for each page using DALL-E 3
                page_images = []  # Store base64 images for web display
                for i, page in enumerate(pages, 1):
                    if page.get('illustration_prompt'):
                        image_data = generate_illustration_dalle(
                            page['illustration_prompt'],
                            i
                        )
                        page['image'] = image_data
                        
                        # Also save base64 for web display
                        if image_data:
                            import base64
                            image_data.seek(0)
                            img_base64 = base64.b64encode(image_data.read()).decode('utf-8')
                            page_images.append({
                                'page': i,
                                'text': page.get('text', ''),
                                'image': img_base64
                            })
                            image_data.seek(0)  # Reset for PDF creation
                
                # Create PDF
                print("📄 Building PDF storybook...")
                pdf_buffer = create_pdf_storybook(
                    pages,
                    request.child_name,
                    request.condition
                )
                
                # Convert to base64 for transmission
                import base64
                pdf_data = base64.b64encode(pdf_buffer.read()).decode('utf-8')
                
                print("✅ Storybook created successfully!")
                
            except Exception as e:
                print(f"❌ Storybook generation failed: {e}")
                import traceback
                traceback.print_exc()
                return {
                    "story": story,
                    "success": True,
                    "condition": request.condition,
                    "pdf_data": None,
                    "message": f"Story generated successfully, but storybook creation failed: {str(e)}"
                }
        
        print(f"✅ Request completed successfully\n")
        
        return {
            "story": story,
            "success": True,
            "condition": request.condition,
            "pdf_data": pdf_data,
            "pages": page_images if request.output_type == "storybook" else None,
            "message": "Generated successfully!" if pdf_data else None
        }
    
    except Exception as e:
        print(f"❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "message": "Cartoon Care - Pediatric Story API with DALL-E 3 Storybook Generation",
        "version": "3.0",
        "dalle_enabled": openai_client.api_key is not None
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "knowledge_base_loaded": vectorstore is not None,
        "openai_configured": openai_client.api_key is not None
    }