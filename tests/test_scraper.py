import unittest
from unittest.mock import patch, Mock
from ..scraping.scraper import *
from datetime import datetime

class TestCodeUnderTest(unittest.TestCase):
    
    # Test scrape_links returns URLs with keywords
    @patch('requests.get')
    def test_scrape_links_returns_urls_with_keywords(self, mock_get):
        # Mock the requests.get call to return a predefined HTML response
        mock_response = mock_get.return_value
        mock_response.content = '''
            <html>
                <body>
                    <a href="/link1_international_student">International Student</a>
                    <a href="/link2_work_permit">Work Permit</a>
                    <a href="/link3_random_link">Random Link</a>
                </body>
            </html>
        '''
        
        # Call the function
        result = scrape_links()

        # Assert that the result contains the expected URLs
        expected_links = [
            'https://www.canada.ca/link1_international_student',
            'https://www.canada.ca/link2_work_permit'
        ]
        self.assertEqual(len(result), len(expected_links))
        self.assertTrue(all(link in result for link in expected_links))

    # Test scrape_links handles empty responses gracefully
    @patch('requests.get')
    def test_scrape_links_handles_empty_responses(self, mock_get):
        # Mock the requests.get call to return an empty HTML response
        mock_response = mock_get.return_value
        mock_response.content = '<html><body></body></html>'
        
        # Call the function
        result = scrape_links()

        # Assert that the result is an empty list
        assert result == []
        
if __name__ == '__main__':
    unittest.main()
