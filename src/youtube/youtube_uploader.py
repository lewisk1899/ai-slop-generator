from gooleapiclient.http import MediaFileUpload

# required package
"""
google-api-python-client
google-auth-oauthlib
google-auth-httplib2
"""

# youtube shorts requirments:
# 1. clip must be less than 3 min in length
# 2. video must be a 9:16 aspect ratio


class YoutubeUploader:

    def upload_video(
        self,
        file_path,
        title,
        description,
        category_id,
        privacy_status="private",  # set private to now for testing
    ):
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": category_id,
            },
            "status": {"privacyStatus": privacy_status},
        }

        media = MediaFileUpload(file_path, resumable=True)

        request = self.youtube.videos().insert(
            part="snippet,status", body=body, media_body=media
        )

        response = request.execute()
        return response
