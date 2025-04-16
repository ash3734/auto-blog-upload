from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
import environ
import logging
import httpx
import os
import json
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG level for more detailed logs

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()

# Initialize OpenAI client with custom timeout and detailed error handling
api_key = env.str('OPENAI_API_KEY').strip()  # Remove any whitespace
logger.error(f"API Key length: {len(api_key)}")

# Get proxy settings from environment or use direct connection
http_proxy = os.environ.get('HTTP_PROXY')
https_proxy = os.environ.get('HTTPS_PROXY')

proxies = None
if http_proxy or https_proxy:
    proxies = {
        'http://': http_proxy,
        'https://': https_proxy,
    }
    logger.error(f"Using proxies: {proxies}")
else:
    logger.error("No proxy settings found, using direct connection")

# Create transport with specific settings
limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
transport = httpx.HTTPTransport(retries=3, limits=limits)

# Set up headers
headers = {
    "Authorization": f"Bearer {api_key}".strip(),
    "Content-Type": "application/json",
    "OpenAI-Beta": "assistants=v1"  # Add beta header
}

# Create custom HTTP client with specific settings
http_client = httpx.Client(
    timeout=httpx.Timeout(
        timeout=60.0,  # Total timeout
        connect=30.0,  # Connection timeout
        read=30.0,     # Read timeout
        write=30.0     # Write timeout
    ),
    transport=transport,
    follow_redirects=True,
    proxies=proxies,
    headers=headers
)

# Initialize OpenAI client
client = OpenAI(
    api_key=api_key.strip(),  # Ensure no whitespace
    http_client=http_client,
    base_url="https://api.openai.com/v1",
    max_retries=3,
    timeout=60.0
)

class AssistantManager:
    def __init__(self):
        self.assistant_id: Optional[str] = None
        self.instructions = """당신은 전문적인 맛집 블로거입니다. 
        주어진 식당 이름을 바탕으로 창의적이고 매력적인 블로그 리뷰 예시를 작성해주세요.
        실제 방문하지 않았으므로, 가상의 경험을 바탕으로 작성합니다.
        
        다음 형식으로 마크다운 글을 작성해주세요:

        1. 제목 (# 사용)
        2. 식당 소개 (상상력을 동원한 간단한 설명)
        3. 분위기 (예상되는 인테리어, 좌석 등 설명)
        4. 추천 메뉴 (식당 이름에서 연상되는 대표 메뉴 제안)
        5. 총평 (상상력을 동원한 전반적인 평가)

        전문적이면서도 친근한 톤으로 작성해주세요.
        이는 테스트용 리뷰이므로, 실제 경험이 아닌 창의적인 예시임을 염두에 두고 작성해주세요."""

    def get_or_create_assistant(self) -> str:
        """Get existing assistant or create a new one"""
        if self.assistant_id:
            return self.assistant_id

        # List existing assistants
        assistants = client.beta.assistants.list(
            order="desc",
            limit=100,
        )

        # Check if our assistant already exists
        for assistant in assistants.data:
            if assistant.name == "Restaurant Reviewer":
                self.assistant_id = assistant.id
                return self.assistant_id

        # Create new assistant if not found
        assistant = client.beta.assistants.create(
            name="Restaurant Reviewer",
            instructions=self.instructions,
            model="gpt-3.5-turbo",
        )
        self.assistant_id = assistant.id
        return self.assistant_id

    async def generate_review(self, restaurant_name: str) -> str:
        """Generate a review using the assistant"""
        # Get or create assistant
        assistant_id = self.get_or_create_assistant()

        # Create a thread
        thread = client.beta.threads.create()

        # Add a message to the thread
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"'{restaurant_name}'이라는 식당의 리뷰를 작성해주세요. 이는 테스트용 리뷰입니다."
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        # Wait for the run to complete
        while run.status in ["queued", "in_progress"]:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        # Get the assistant's response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        review = messages.data[0].content[0].text.value

        return review

# Create singleton instance
assistant_manager = AssistantManager()

# Create your views here.

class HelloWorldView(APIView):
    def get(self, request):
        return Response({"message": "Hello, World!"}, status=status.HTTP_200_OK)

class PreviewView(APIView):
    async def post(self, request):
        try:
            logger.error("Request received")
            restaurant_name = request.data.get('restaurant_name')
            
            logger.error(f"Restaurant name: {restaurant_name}")
            
            if not restaurant_name:
                return Response(
                    {"error": "restaurant_name은 필수 항목입니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate review using the assistant
            blog_post = await assistant_manager.generate_review(restaurant_name)
            logger.error("Blog post generated successfully")

            return Response({
                "preview": blog_post
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in PreviewView: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TestOpenAIView(APIView):
    def get(self, request):
        try:
            logger.error("Testing OpenAI connection...")
            logger.error(f"Using API base: {client.base_url}")
            
            try:
                # First, try a direct HTTP request
                logger.error("Testing direct HTTP request...")
                direct_response = http_client.get("https://api.openai.com/v1/models")
                logger.error(f"Direct request status: {direct_response.status_code}")
                logger.error(f"Direct request headers: {dict(direct_response.headers)}")
                logger.error(f"Direct request response: {direct_response.text}")
                
                if direct_response.status_code == 401:
                    logger.error("Authentication failed. Checking API key format...")
                    if not api_key.startswith('sk-'):
                        logger.error("API key format appears invalid")
                        return Response({"error": "Invalid API key format"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # If direct request works, try the OpenAI client
                logger.error("Testing OpenAI client...")
                models = client.models.list()
                logger.error("Successfully retrieved models list")
                
                # If models list works, try chat completion
                logger.error("Testing chat completion...")
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": "Hello, are you working?"}
                    ]
                )
                return Response({"message": response.choices[0].message.content}, status=status.HTTP_200_OK)
            except httpx.ConnectError as e:
                logger.error(f"Connection error details: {str(e)}")
                logger.error(f"Connection error type: {type(e)}")
                return Response({"error": f"Connection error details: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                logger.error(f"OpenAI API error details: {str(e)}")
                logger.error(f"Error type: {type(e)}")
                return Response({"error": f"OpenAI API error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"General error: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
