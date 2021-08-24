#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# External imports
import functools
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
import urllib
from viaa.configuration import ConfigParser

config = ConfigParser()


class AuthenticationException(Exception):
    """Exception raised when authentication fails."""

    pass


class MediahavenClient:
    def __init__(self, configParser: ConfigParser = None):
        self.config: dict = configParser.app_cfg
        self.token_info = None
        self.url = self.config["mediahaven"]["host"]

    def __authenticate(function):
        @functools.wraps(function)
        def wrapper_authenticate(self, *args, **kwargs):
            if not self.token_info:
                self.token_info = self.__get_token()
            try:
                return function(self, *args, **kwargs)
            except AuthenticationException:
                self.token_info = self.__get_token()
            return function(self, *args, **kwargs)

        return wrapper_authenticate

    def __get_token(self) -> str:
        """Gets an OAuth token that can be used in mediahaven requests to
        authenticate."""
        username: str = self.config["mediahaven"]["username"]
        password: str = self.config["mediahaven"]["password"]
        url: str = self.url + "/oauth/access_token"
        payload = {"grant_type": "password"}

        try:
            r = requests.post(
                url,
                auth=HTTPBasicAuth(username.encode("utf-8"), password.encode("utf-8")),
                data=payload,
            )

            if r.status_code != 201:
                raise RequestException(f"Failed to get a token. Status: {str(r.text)}")
            token_info = r.json()
        except RequestException as e:
            raise e
        return token_info

    def _construct_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token_info['access_token']}",
            "Accept": "application/vnd.mediahaven.v2+json",
        }

    @__authenticate
    def get_media_object_id(self, pid: str) -> str:
        """Get MediaObjectId from pid.

        Params:
            pid: pid of the essence

        Returns:
            MediaObjectId
        """

        try:
            headers = self._construct_headers()

            # Construct query as '+(query_key:"value")'
            query = f'+(dc_identifier_localid:"{pid}")'

            params_dict: dict = {
                "q": query,
            }

            # Encode the spaces in the query parameters as %20 and not +
            params = urllib.parse.urlencode(params_dict, quote_via=urllib.parse.quote)

            # Send the GET request
            response = requests.get(
                self.url + "/media/", headers=headers, params=params
            )

            if response.status_code == 401:
                # AuthenticationException triggers a retry with a new token
                print("Auth exception" + response.text)
                raise AuthenticationException(response.text)

            if response.status_code == 404:
                print(f"MediaObjectId not found for pid {pid}")
                raise Exception(response.text)

            media_object_id = response.json()["MediaDataList"][0]["Internal"][
                "MediaObjectId"
            ]
            return media_object_id

        except Exception as exception:
            print(f"Error fetching MediaObjectId for pid {pid}: {str(exception)}")

    @__authenticate
    def export_essence(self, pid) -> dict:
        """
        Export essence from MediaHaven to export location.

        Params:
            pid: pid of the essence to be exported

        Returns:
            exportjob {
                "exportId" : <EXPORTID>,
                "status" : <STATUS>,
                "downloadUrl" : ""
            }
        """
        export_location_id = self.config["mediahaven"]["export_location_id"]
        url = self.url + "/media/" + pid + "/export/" + export_location_id

        try:
            headers = self._construct_headers()
            response = requests.post(url, headers=headers)

            if response.status_code == 401:
                # AuthenticationException triggers a retry with a new token
                print("Auth exception" + response.text)
                raise AuthenticationException(response.text)

            # Response contains a list of export jobs
            return response.json()[0]

        except Exception as exception:
            print(f"Error exporting essence with for pid {pid}: {str(exception)}")

    @__authenticate
    def get_metadata(self, media_object_id):
        """
        Get metadata for a file, using the file's media_object_id
        """

        url = self.url + "/media/" + media_object_id

        try:
            headers = self._construct_headers()
            response = requests.get(url, headers=headers)
            response_json = response.json()

            if "status" in response_json and response_json["status"] == 400:
                raise Exception(
                    f"No metadata found for media_object_id {media_object_id}"
                )

            return response_json

        except Exception as exception:
            print(
                f"Error getting metadata for media_object_id {media_object_id}: \
                {str(exception)}"
            )
