import re
class UserHelper:
    @classmethod
    def extract_user_name(klass,user):
        return re.sub('@.*$', '', user.email())
