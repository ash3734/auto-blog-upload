from django.http import JsonResponse
from rest_framework.views import APIView
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class AutoReplyView(APIView):
    def get(self, request, *args, **kwargs):
        # Set up Selenium WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        try:
            # Example: Open a webpage
            driver.get('https://example.com')
            title = driver.title
            
            # Return the page title as a response
            return JsonResponse({'title': title})
        finally:
            driver.quit() 