"""
Subpackage for interacting with Microsoft SQL Server database
"""

from . import connection
from . import users
from . import utils

"""
## users:

get user id in login request, insert user entry if doesn't exist
check that user exists in verify_users
 - will need to check role ultimately


"""