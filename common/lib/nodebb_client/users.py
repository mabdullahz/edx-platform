from pynodebb.api.users import User


class ForumUser(User):
    """
    Added custom methods to the default User class of pynodebb package
    """

    def join(self, group_name, user_name, uid=1, **kwargs):
        """
        Make user a participant of specified group
        """
        payload = {'name': group_name, 'username': user_name, '_uid': uid}
        return self.client.post('/api/v2/users/join', **payload)

    def create(self, username, **kwargs):
        """
        Create a user on Nodebb
        """
        kwargs.update({'username': username})
        return self.client.post('/api/v2/users/create', **kwargs['kwargs'])

    def activate(self, username, active, **kwargs):
        """
        Activate a given user
        """
        payload = {'username': username, 'active': active, "_uid": 1}
        return self.client.post('/api/v2/users/activate', **payload)

    def update_profile(self, username, **kwargs):
        """
        Updated user profile by providing fields in kwargs
        """
        kwargs['kwargs']['username'] = username
        return self.client.post('/api/v2/users/update', **kwargs['kwargs'])

    def delete_user(self, username, kwargs):
        """
        Delete user from NodBB database
        """
        kwargs['username'] = username
        kwargs['_uid'] = 1
        return self.client.delete('/api/v2/user/delete', **kwargs)

    def update_onboarding_surveys_status(self, username, email_pref='n'):
        """
        Update NodeBB when user successfully completed all required onboarding surveys
        """
        return self.client.get('/api/v2/users/update-visibility-status?username=%s&emailPref=%s' %
                               (username, email_pref))
