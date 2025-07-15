import os

urls = dict(
   tvcoins=os.getenv("TVCOINS_URL", "https://www.tradingview.com/tvcoins/details/"),
   username_hint=os.getenv("USERNAME_HINT_URL", "https://www.tradingview.com/username_hint/"),
   list_users=os.getenv("LIST_USERS_URL", "https://www.tradingview.com/pine_perm/list_users/"),
   modify_access=os.getenv("MODIFY_ACCESS_URL", "https://www.tradingview.com/pine_perm/modify_user_expiration/"),
   add_access=os.getenv("ADD_ACCESS_URL", "https://www.tradingview.com/pine_perm/add/"),
   remove_access=os.getenv("REMOVE_ACCESS_URL", "https://www.tradingview.com/pine_perm/remove/"),
   signin=os.getenv("SIGNIN_URL", "https://www.tradingview.com/accounts/signin/")
)
