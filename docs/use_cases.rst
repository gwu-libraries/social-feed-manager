.. Social Feed Manager Use Cases

Use Cases
=========

Definitions
-----------

A *TwitterUser* in SFM is the entity used to collect
tweets tweeted by the corresponding account in Twitter.

The fundamental, unique, unchanging identifier for a Twitter account is
its numeric UID.  The account owner can change the name of the account,
but the UID will never change.

Each TwitterUser is intended to map one-to-one to a Twitter account.

Given the rules above, we can derive two rules:

* A TwitterUser account should never be associated with tweets from more than
  one UID.
* A TwitterUser account's UID should never change.


Lifecycle of a TwitterUser
--------------------------

A TwitterUser in SFM exists in one of three states:

* *Nonexistence (Pre-creation/Post-deletion)*
* *Active*
* *Inactive*

An account in Twitter exists in one of three states:

* *Pre-creation*
* *Active/Public* - Tweets are visibile to anyone
* *Active/Protected* - Tweets are only visible to this account's Twitter followers
* *Deactivated/Deleted* - If an owner deactivates a Twitter account, Twitter
  places it on a quque for permanent deletion.



State Transitions
-----------------

**TwitterUser Creation**  The SFM user provides the username of the Twitter
account to map to this SFM TwitterUser.  SFM looks up the Twitter account's
UID by the username provided.  If:

* the username matches a Twitter account's username, and
* the Twitter account's UID is not already associated with any TwitterUser
then SFM will create the TwitterUser.
*If the name does not match any Twitter account OR the UID is already
associated with a TwitterUser, then SFM will
not create the TwitterUser, even an in Inactive state.*

**Inactivation of Active TwitterUser**  An SFM user marks an Active TwitterUser as Inactive.  This transition is always allowed.

**Activation of Inactive TwitterUser**  An SFM user marks an Inactive TwitterUser as Active.  

**More to come here**

Complex Use Cases
-----------------

**???**
