import httplib2
import os
import random
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

"""
Client secrets format (app credientials):
{
  "installed": {
    "client_id": "837647042410-75ifg...usercontent.com",
    "client_secret":"asdlkfjaskd",
    "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token"
  }
}

oauth2.json (user credentials):
{
  "access_token": "ya29.a0AfH6SM...",
  "refresh_token": "1//04uKz...",
  "token_expiry": "2025-11-09T20:21:02Z",
  "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
  "client_secret": "YOUR_CLIENT_SECRET",
  "scopes": ["https://www.googleapis.com/auth/youtube.upload"]
}

usage: 
video_uploader = YoutubeUploader(video_path, video_title, video_desc, category, privacy_status)
video_uploader.upload()

"""


class YoutubeUploader:
    def __init__(
        self,
        video_path: str,
        video_title: str,
        video_desc: str,
        category: int = 22,
        privacy_status: str = "public",
    ):
        # Maximum amount of times the uploader will try to upload until it gives up
        self.MAX_RETRYS = 3
        # Always retry when this exception is raised
        self.RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

        # Always retry when one of these status codes are raised
        self.RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
        self.CLIENT_SECRETS = "client_secrets.json"
        self.YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
        self.YOUTUBE_API_SERVICE_NAME = "youtube"
        self.YOUTUBE_API_VERSION = "v3"

        self.VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

        self.ERROR_MESSAGE = """
        Please visit https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
        to set up the client_secrets.json.
        """

        # Store arguments
        self.video_path = video_path
        self.video_desc = video_desc
        self.video_title = video_title
        self.category = category
        self.privacy_status = (
            privacy_status
            if privacy_status in self.VALID_PRIVACY_STATUSES
            else "public"
        )

    def upload(self):
        if not os.path.exists(self.video_path):
            print("Video path not found. Exiting")
            return
        youtube = self.get_authenticated_service()
        try:
            self.initialize_upload(youtube)
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occured: {e.content}")

    def get_authenticated_service(self):
        flow = flow_from_clientsecrets(
            self.CLIENT_SECRETS,
            scope=self.YOUTUBE_UPLOAD_SCOPE,
            message=self.ERROR_MESSAGE,
        )

        storage = Storage(f"{os.path.splitext(sys.argv[0])[0]}-oauth2.json")
        credentials = storage.get()

        if credentials is None or credentials.invalid:

            parser = argparser
            parser.add_argument(
                "--noauth_local_webserver", action="store_true", default=True
            )
            parser.add_argument(
                "--auth_host_port", default=[8080, 8090], type=int, nargs="*"
            )
            parser.add_argument("--logging_level", default="INFO")

            args = parser.parse_args([])

            credentials = run_flow(flow, storage, args)
        return build(
            self.YOUTUBE_API_SERVICE_NAME,
            self.YOUTUBE_API_VERSION,
            http=credentials.authorize(httplib2.Http()),
        )

    def initialize_upload(self, youtube):
        tags = None
        body = dict(
            snippet=dict(
                title=self.video_title,
                description=self.video_desc,
                tags=tags,
                categoryId=self.category,
            ),
            status=dict(privacyStatus=self.privacy_status),
        )
        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(self.video_path, chunksize=-1, resumable=True),
        )

        self.resumable_upload(insert_request)

    def resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if "id" in response:
                        print(
                            "Video id '%s' was successfully uploaded." % response["id"]
                        )
                    else:
                        exit(
                            "The upload failed with an unexpected response: %s"
                            % response
                        )
            except HttpError as e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    error = "A retriable HTTP error %d occurred:\n%s" % (
                        e.resp.status,
                        e.content,
                    )
                else:
                    raise
            except self.RETRIABLE_EXCEPTIONS as e:
                error = "A retriable error occurred: %s" % e

            if error is not None:
                print(error)
                retry += 1
                if retry > self.MAX_RETRYS:
                    exit("No longer attempting to retry.")

                max_sleep = 2**retry
                sleep_seconds = random.random() * max_sleep
                print("Sleeping %f seconds and then retrying..." % sleep_seconds)
                time.sleep(sleep_seconds)
