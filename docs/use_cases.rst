.. Social Feed Manager Use Cases

Use Cases
=========

Definitions
-----------

A *TwitterUser* in SFM is the entity used to collect
tweets tweeted by the corresponding account in Twitter.

The fundamental, unique, unchanging 
identifier for a Twitter account is
its numeric UID.  The owner of a Twitter account might change the account's
name, but the UID will never change.

Each TwitterUser is intended to map one-to-one to a Twitter account.

Given the rules above, we can derive two rules:

* A TwitterUser account should never be associated with tweets from more than
  one UID.
* A TwitterUser account's UID should never change.


Lifecycle of a TwitterUser
--------------------------

A TwitterUser in SFM exists in one of three states:

* *Nonexistence (Pre-creation/Post-deletion)*
* *Active* - SFM will attempt to collect new tweets for this TwitterUser, every time the
  *user_timeline* script is run.
* *Inactive* - The TwitterUser is still in SFM, but no new tweets will be collected while the
  TwitterUser is inactive.

An account in Twitter exists in one of three states:

* *Pre-creation*
* *Active/Public* - Tweets are visibile to anyone
* *Active/Protected* - Tweets are only visible to this account's Twitter followers
* *Deactivated/Deleted* - If an owner deactivates a Twitter account, Twitter
  places it on a queue to be permanently deleted after 30 days.



State Transitions
-----------------

**TwitterUser Creation**  The SFM user provides the username of the Twitter
account to map to this SFM TwitterUser.  SFM looks up the Twitter account's
UID by the username provided.  If:

* the username matches a Twitter account's username, and
* the Twitter account's UID is not already associated with any TwitterUser
then SFM will create the TwitterUser.  The SFM user may create the new
TwitterUser as either Active or Inactive.

*If the name does not match any Twitter account OR the UID is already
associated with a TwitterUser, then SFM will
not create the TwitterUser, even an in Inactive state.*

**Inactivation of Active TwitterUser**  An SFM user marks an Active TwitterUser as Inactive.  This transition is always allowed.  Inactive TwitterUsers are still shown on the SFM page listing users,
and CSV extracts

**Activation of Inactive TwitterUser**  An SFM user marks an Inactive
TwitterUser as Active.  SFM looks up the corresponding Twitter account by
the UID of the TwitterUser.
If the UID is valid, it updates the TwitterUser's name if differs from the current
name of the Twitter account, and saves the TwitterUser as Active.
If the UID is not found, which may occur if the Twitter account has been
deactivated, then SFM does not allow the TwitterUser to be saved as Active.

**Deletion of a TwitterUser**  An SFM administrative user deletes a TwitterUser.  This is always allowed.  However, it is important to note that
*all TwitterItems associated with this TwitterUser will also be deleted.*


**Name Change** What if the owner of a Twitter account changes the name of the account?
If the TwitterUser in SFM was created to collect tweets from this Twitter account, it should
continue to do so, since the UID never changes.  However, the name of the TwitterUser may
temporarily still show the old name of the Twitter account.  If a cron job has been set up
to run update_usernames, then the name of the TwitterUser will automatically be updated to
match the new Twitter account name the next time update_username is run.  When update_username
observes a name change, the old name will be appended to the TwitterUser's *former_names*,
along with the date and time that the change was detected by update_usernames.  As an example,
if a Twitter account named ``NYTimes`` was then changed to ``NewYorkTimes``, then
the update_usernames script would update the name of the TwitterUser, and would also append
to *former_names* so it might have a value like ``{"Thu Jan 16 13:48:56 2014": "NYTimes"}``

**Twitter Account Goes Protected** What if the owner of a Twitter account
marks the account as protected?

If the ``TWITTER_DEFAULT_USERNAME`` configured in local_settings.py
is a Twitter account which is following the protected Twitter account in
question, then SFM will continue to be able to download tweets from that
account.

If this is not the case, then user_timeline jobs will
encounter errors when attempting to retrieve new tweets for the account.
These errors will be recorded in the TwitterUserTimelineErrors table.

**Twitter Account Deletion** What if the owner of a Twitter account deletes
the account?

If the owner of a Twitter account deletes the account and there is an
active TwitterUser mapped to the account, then user_timeline jobs will
encounter errors when attempting to retrieve new tweets for the account.
These errors will be recorded in the TwitterUserTimelineErrors table.
