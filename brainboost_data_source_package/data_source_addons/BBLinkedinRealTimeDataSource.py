import textwrap
from brainboost_data_source_package.data_source_abstract.BBRealTimeDataSource import BBRealTimeDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger

class BBLinkedInRealTimeDataSource(BBRealTimeDataSource):
    def __init__(self, params=None):
        # Ensure params is a dictionary and set a default time_interval if not provided.
        if params is None:
            params = {}
        if 'time_interval' not in params:
            params['time_interval'] = 10   # Default to 10 minutes
        super().__init__(params=params)
        self.time_interval = params['time_interval']

    def fetch(self):
        # This code will take screenshots and extract LinkedIn real-time data.
        BBLogger.log("Starting real-time LinkedIn processing.")
        # [Your real-time fetching implementation here]
        pass

    def get_icon(self):
        """Return the SVG code for the LinkedIn real-time icon."""
        # Use textwrap.dedent to remove extra indentation.
        svg = textwrap.dedent("""\
            <svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" fill="none">
              <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
              <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
              <g id="SVGRepo_iconCarrier">
                <path fill="#0A66C2" d="M12.225 12.225h-1.778V9.44c0-.664-.012-1.519-.925-1.519-.926 0-1.068.724-1.068 1.47v2.834H6.676V6.498h1.707v.783h.024c.348-.594.996-.95 1.684-.925 1.802 0 2.135 1.185 2.135 2.728l-.001 3.14zM4.67 5.715a1.037 1.037 0 01-1.032-1.031c0-.566.466-1.032 1.032-1.032.566 0 1.031.466 1.031 1.032 0 .566-.466 1.032-1.031 1.032zm.889 6.51h-1.78V6.498h1.78v5.727zM13.11 2H2.885A.88.88 0 002 2.866v10.268a.88.88 0 00.885.866h10.226a.882.882 0 00.889-.866V2.865a.88.88 0 00-.889-.864z"/>
              </g>
            </svg>
        """)
        return svg

    def get_connection_data(self):
        """
        Return the connection type and required fields for the LinkedIn real-time data source.
        """
        return {
            "connection_type": "LinkedIn",
            "fields": ["brainboost_cookie_linkedin_li_at", "brainboost_cookie_linkedin_jsession"]
        }


