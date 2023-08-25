""" Copyright start
  Copyright (C) 2008 - 2023 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

import requests, json
from connectors.core.connector import get_logger, ConnectorError

logger = get_logger('jira_insight_db')


def get_config(config):
    try:
        if config is not None:
            jira_server_url = config.get('server_url')
            jira_username = config.get('username')
            jira_token = config.get('token')
            verify_ssl = config.get('verify_ssl')
            return jira_server_url, jira_username, jira_token, verify_ssl
    except Exception as Err:
        logger.warn('Error occured while extracting conf :[{0}] '.format(Err))
        raise ConnectorError(Err)


def make_api_call(config, method='GET', endpoint=None, json=None, headers=None, params=None, data=None):
    server, username, token, verify_ssl = get_config(config)
    if server.startswith('https://'):
        server = server.strip('/') + '/rest/insight/1.0'
    else:
        server = server + '/rest/insight/1.0'
    if not headers:
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
    if endpoint:
        url = '{0}{1}'.format(server, endpoint)
    else:
        url = server
    logger.info('Request URL {}'.format(url))
    try:
        response = requests.request(method=method, url=url, auth=(username, token), headers=headers, data=data, params=params, verify=verify_ssl)
        if response.ok:
            return response.json()
        elif response.status_code == 401:
            logger.info('Unauthorized: Invalid credentials')
            raise ConnectorError('Unauthorized: Invalid credentials')
        else:
            logger.info(
                'Fail To request API {0} response is : {1} with reason: {2}'.format(str(url), str(response.content),
                                                                                    str(response.reason)))
            raise ConnectorError(
                'Fail To request API {0} response is :{1} with reason: {2}'.format(str(url), str(response.content),
                                                                                   str(response.reason)))
    except requests.exceptions.SSLError as e:
        logger.exception('{}'.format(e))
        raise ConnectorError('{}'.format('SSL certificate validation failed'))
    except requests.exceptions.ConnectionError as e:
        logger.exception('{}'.format(e))
        raise ConnectorError('{}'.format('The request timed out while trying to connect to the remote server'))
    except Exception as e:
        logger.exception('{}'.format(e))
        raise ConnectorError('{}'.format(e))


def check_health(config):
    try:
        if make_api_call(config=config, endpoint='/config/statustype'):
            return True
    except Exception as Err:
        logger.exception('Error occured while connecting server: {}'.format(str(Err)))
        raise ConnectorError('Error occured while connecting server: {}'.format(Err))


def create_object(config, params):
    try:
        params = {k: v for k, v in params.items() if v is not None and v != ''}
        endpoint = "/object/create"
        other_fields = params.get('other_fields')
        if 'objectTypeId' in other_fields:
            payload = other_fields
        else:
            payload = {
                "objectTypeId": params.get('objectTypeId'),
                "attributes": [
                    {
                        "objectTypeAttributeId": params.get('objectTypeAttributeId'),
                        "objectAttributeValues": [
                            {
                                "value": params.get('object_attribute_value')
                            }
                        ]
                    }
                ]
            }
        response = make_api_call(config, method='POST', endpoint=endpoint, data=json.dumps(payload))
        return response
    except Exception as Err:
        raise ConnectorError(Err)


def update_object(config, params):
    try:
        params = {k: v for k, v in params.items() if v is not None and v != ''}
        endpoint = "/object/{object_id}".format(object_id=params.get('object_id'))
        other_fields = params.get('other_fields')
        if 'objectTypeId' in other_fields:
            payload = other_fields
        else:
            payload = {
                "objectTypeId": params.get('objectTypeId'),
                "attributes": [
                    {
                        "objectTypeAttributeId": params.get('objectTypeAttributeId'),
                        "objectAttributeValues": [
                            {
                                "value": params.get('object_attribute_value')
                            }
                        ]
                    }
                ]
            }
        response = make_api_call(config, method='PUT', endpoint=endpoint, data=json.dumps(payload))
        return response
    except Exception as Err:
        raise ConnectorError(Err)


def get_assets(config, params):
    try:
        params = {k: v for k, v in params.items() if v is not None and v != ''}
        endpoint = "/iql/objects"
        response = make_api_call(config, endpoint=endpoint, params=params)
        return response
    except Exception as Err:
        raise ConnectorError(Err)


def get_asset_details(config, params):
    try:
        asset_id = params.get('asset_id')
        endpoint = "/object/{id}".format(id=asset_id)
        response = make_api_call(config, endpoint=endpoint)
        return response
    except Exception as Err:
        raise ConnectorError(Err)


def get_asset_attributes(config, params):
    try:
        asset_id = params.get('asset_id')
        endpoint = "/object/{id}/attributes".format(id=asset_id)
        response = make_api_call(config, endpoint=endpoint)
        return response
    except Exception as Err:
        raise ConnectorError(Err)


def get_asset_history(config, params):
    try:
        asset_id = params.get('asset_id')
        params = {k: v for k, v in params.items() if v is not None and v != ''}
        params.pop('asset_id')
        endpoint = "/object/{id}/history".format(id=asset_id)
        response = make_api_call(config, endpoint=endpoint, params=params)
        return response
    except Exception as Err:
        raise ConnectorError(Err)


def get_asset_reference_info(config, params):
    try:
        asset_id = params.get('asset_id')
        endpoint = "/object/{id}/referenceinfo".format(id=asset_id)
        response = make_api_call(config, endpoint=endpoint)
        return response
    except Exception as Err:
        raise ConnectorError(Err)


def get_asset_connected_tickets(config, params):
    try:
        asset_id = params.get('asset_id')
        endpoint = "/objectconnectedtickets/{id}".format(id=asset_id)
        response = make_api_call(config, endpoint=endpoint)
        return response
    except Exception as Err:
        raise ConnectorError(Err)


operations = {
    'create_object': create_object,
    'update_object': update_object,
    'get_assets': get_assets,
    'get_asset_details': get_asset_details,
    'get_asset_attributes': get_asset_attributes,
    'get_asset_history': get_asset_history,
    'get_asset_reference_info': get_asset_reference_info,
    'get_asset_connected_tickets': get_asset_connected_tickets
}
