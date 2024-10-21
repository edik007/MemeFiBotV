from random import randint

from aiohttp import ClientSession
from asyncio import sleep

from bot.exceptions import InvalidProtocol
from bot.utils.boosts import FreeBoostType, UpgradableBoostType
from bot.utils.graphql import OperationName, Query
from bot.utils import logger


class MemeFiApi:

    GRAPHQL_URL: str = "https://api-gw-tg.memefi.club/graphql"
    session_name: str = "UnknownSession"

    def __init__(self, url: str = None, session_name: str = None) -> None:
        if url:
            self.GRAPHQL_URL = url
        if session_name:
            self.session_name = session_name


    async def get_access_token(self, http_client: ClientSession, tg_web_data: dict[str]):
        for _ in range(2):
            try:
                response = await http_client.post(url=self.GRAPHQL_URL, json=tg_web_data)
                response.raise_for_status()

                response_json = await response.json()

                if 'errors' in response_json:
                    raise InvalidProtocol(f'get_access_token msg: {response_json["errors"][0]["message"]}')

                access_token = response_json.get('data', {}).get('telegramUserLogin', {}).get('access_token', '')

                if not access_token:
                    await sleep(delay=5)
                    continue

                return access_token
            except Exception as error:
                logger.error(f"{self.session_name} | ❗️ Unknown error while getting Access Token: {error}")
                await sleep(delay=15)

        return ""

    async def get_profile_data(self, http_client: ClientSession):
        try:
            json_data = {
                'operationName': OperationName.QUERY_GAME_CONFIG,
                'query': Query.QUERY_GAME_CONFIG,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()
            response_json = await response.json()

            if 'errors' in response_json:
                raise InvalidProtocol(f'get_profile_data msg: {response_json["errors"][0]["message"]}')

            profile_data = response_json['data']['telegramGameGetConfig']

            return profile_data
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️Unknown error while getting Profile Data: {error}")
            await sleep(delay=9)

    async def get_telegram_me(self, http_client: ClientSession):
        try:
            json_data = {
                'operationName': OperationName.QueryTelegramUserMe,
                'query': Query.QueryTelegramUserMe,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            response_json = await response.json()

            if 'errors' in response_json:
                raise InvalidProtocol(f'get_telegram_me msg: {response_json["errors"][0]["message"]}')

            me = response_json['data']['telegramUserMe']

            return me
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error while getting Telegram Me: {error}")
            await sleep(delay=3)

            return {}

    async def wallet_check(self, http_client: ClientSession):
        try:
            json_data = {
                'operationName': OperationName.TelegramMemefiWallet,
                'query': Query.TelegramMemefiWallet,
                'variables': {}
            }
            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response_json = await response.json()
            no_wallet_response = {'data': {'telegramMemefiWallet': None}}
            if response_json == no_wallet_response:
                none_wallet = "-"
                linea_wallet = none_wallet
                return linea_wallet
            else:
                linea_wallet = response_json.get('data', {}).get('telegramMemefiWallet', {}).get('walletAddress', {})
                return linea_wallet
        except Exception as error:
                logger.error(f"{self.session_name} | ❗️ Unknown error when Get Wallet: {error}")
                return None

    async def apply_boost(self, http_client: ClientSession, boost_type: FreeBoostType):
        try:
            json_data = {
                'operationName': OperationName.telegramGameActivateBooster,
                'query': Query.telegramGameActivateBooster,
                'variables': {
                    'boosterType': boost_type
                }
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error while Apply {boost_type} Boost: {error}")
            await sleep(delay=9)

            return False

    async def upgrade_boost(self, http_client: ClientSession, boost_type: UpgradableBoostType):
        try:
            json_data = {
                'operationName': OperationName.telegramGamePurchaseUpgrade,
                'query': Query.telegramGamePurchaseUpgrade,
                'variables': {
                    'upgradeType': boost_type
                }
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            response_json = await response.json()

            if 'errors' in response_json:
                raise InvalidProtocol(f'upgrade_boost msg: {response_json["errors"][0]["message"]}')

            return True
        except Exception:
            return False

    async def set_next_boss(self, http_client: ClientSession):
        try:
            json_data = {
                'operationName': OperationName.telegramGameSetNextBoss,
                'query': Query.telegramGameSetNextBoss,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()
            response_json = await response.json()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️Unknown error while Setting Next Boss: {error}")
            await sleep(delay=9)

            return False

    async def send_taps(self, http_client: ClientSession, nonce: str, taps: int):
        try:
            vectorArray = []
            for tap in range(taps):
                """ check if tap is greater than 4 or less than 1 and set tap to random number between 1 and 4"""
                if tap > 4 or tap < 1:
                    tap = randint(1, 4)
                vectorArray.append(tap)

            vector = ",".join(str(x) for x in vectorArray)
            json_data = {
                'operationName': OperationName.MutationGameProcessTapsBatch,
                'query': Query.MutationGameProcessTapsBatch,
                'variables': {
                    'payload': {
                        'nonce': nonce,
                        'tapsCount': taps,
                        'vector': vector
                    },
                }
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            response_json = await response.json()

            if response.status != 200:
                return response.status

            if 'errors' in response_json:
                raise InvalidProtocol(f'send_taps msg: {response_json["errors"][0]["message"]}')

            profile_data = response_json['data']['telegramGameProcessTapsBatch']
            return profile_data
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error when Tapping: {error}")
            await sleep(delay=9)

    async def get_campaigns(self, http_client: ClientSession):
        try:
            json_data = {
                'operationName': "CampaignLists",
                'query': Query.CampaignLists,
                'variables': {}
            }
            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            data = await response.json()

            if 'errors' in data:
                logger.error(f"{self.session_name} | Error while getting campaigns: {data['errors'][0]['message']}")
                return None

            campaigns = data.get('data', {}).get('campaignLists', {}).get('normal', [])
            return [campaign for campaign in campaigns if 'youtube' in campaign.get('description', '').lower()]

        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while getting campaigns: {str(e)}")
            return {}

    async def verify_campaign(self, http_client: ClientSession, task_id: str):
        try:
            json_data = {
                'operationName': "CampaignTaskToVerification",
                'query': Query.CampaignTaskToVerification,
                'variables': {'taskConfigId': task_id}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            data = await response.json()

            if 'errors' in data:
                logger.error(f"{self.session_name} | Error while verifying task: {data['errors'][0]['message']}")
                return None

            return data.get('data', {}).get('campaignTaskMoveToVerificationV2')
        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while verifying task: {str(e)}")
            return None

    async def complete_task(self, http_client: ClientSession, user_task_id: str, code: str = None):
        try:
            json_data = {
                'operationName': "CampaignTaskMarkAsCompleted",
                'query': Query.CampaignTaskMarkAsCompleted,
                'variables': {'userTaskId': user_task_id, 'verificationCode': str(code)} if code \
                    else  {'userTaskId': user_task_id}
            }
            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)

            response.raise_for_status()

            data = await response.json()


            if 'errors' in data:
                logger.error(f"{self.session_name} | Error while completing task: {data['errors'][0]['message']}")
                return None

            return data.get('data', {}).get('campaignTaskMarkAsCompleted')

        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while completing task: {str(e)}")
            return None

    async def get_tasks_list(self, http_client: ClientSession, campaigns_id: str):
        try:
            json_data = {
                'operationName': "GetTasksList",
                'query': Query.GetTasksList,
                'variables': {'campaignId': campaigns_id}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            data = await response.json()

            if 'errors' in data:
                logger.error(f"{self.session_name} | Error while getting tasks: {data['errors'][0]['message']}")
                return None

            return data.get('data', {}).get('campaignTasks', [])

        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while getting tasks: {str(e)}")
            return None

    async def get_task_by_id(self, http_client: ClientSession, task_id: str):
        try:
            json_data = {
                'operationName': "GetTaskById",
                'query': Query.GetTaskById,
                'variables': {'taskId': task_id}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            data = await response.json()

            if 'errors' in data:
                logger.error(
                    f"{self.session_name} | Error while getting task by id: {data['errors'][0]['message']}")
                return None

            return data.get('data', {}).get('campaignTaskGetConfig')
        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while getting task by id: {str(e)}")
            return None

    async def get_clan(self, http_client: ClientSession):
        try:
            json_data = {
                'operationName': OperationName.ClanMy,
                'query': Query.ClanMy,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()
            response_json = await response.json()

            data = response_json['data']['clanMy']
            if data and data['id']:
                return data['id']
            else:
                return False

        except Exception as error:
            logger.error(f"{self.session_name} | ❗️Unknown error while get clan: {error}")
            await sleep(delay=9)
            return False

    async def leave_clan(self, http_client: ClientSession):
        try:
            json_data = {
                'operationName': OperationName.Leave,
                'query': Query.Leave,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()
            response_json = await response.json()
            if response_json['data']:
                if response_json['data']['clanActionLeaveClan']:
                    return True

        except Exception as error:
            logger.error(f"{self.session_name} | ❗️Unknown error while clan leave: {error}")
            await sleep(delay=9)
            return False

    async def join_clan(self, http_client: ClientSession):
        try:
            json_data = {
                'operationName': OperationName.Join,
                'query': Query.Join,
                'variables': {
                    'clanId': '71886d3b-1186-452d-8ac6-dcc5081ab204'
                }
            }

            while True:
                response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
                response.raise_for_status()
                response_json = await response.json()
                if response_json['data']:
                    if response_json['data']['clanActionJoinClan']:
                        return True
                elif response_json['errors']:
                    await sleep(2)
                    return False

        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error while clan join: {error}")
            await sleep(delay=9)
            return False

    async def start_bot(self, http_client: ClientSession):
        try:
            json_data = {
                'operationName': OperationName.TapbotStart,
                'query': Query.TapbotStart,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error while Starting Bot: {error}")
            await sleep(delay=9)

            return False

    async def claim_bot(self, http_client: ClientSession):
        try:
            json_data = {
                'operationName': OperationName.TapbotClaim,
                'query': Query.TapbotClaim,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()
            response_json = await response.json()
            data = response_json['data']["telegramGameTapbotClaim"]
            return {"isClaimed": False, "data": data}
        except Exception as error:
            return {"isClaimed": True, "data": None}

    async def claim_referral_bonus(self, http_client: ClientSession):
        try:
            json_data = {
                'operationName': OperationName.Mutation,
                'query': Query.Mutation,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error while Claiming Referral Bonus: {error}")
            await sleep(delay=9)

            return False