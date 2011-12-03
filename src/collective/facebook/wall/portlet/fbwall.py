from zope.interface import implements
from zope.interface import alsoProvides

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from zope.formlib import form
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.registry.interfaces import IRegistry
from zope.schema.interfaces import IContextSourceBinder

from collective.facebook.wall import _
from collective.facebook.wall.config import GRAPH_URL

import DateTime
import json
import urllib

def FacebookAccounts(context):
    registry = getUtility(IRegistry)
    accounts = registry['collective.facebook.accounts']
    if accounts:
        keys = accounts.keys()
    else:
        keys = []

    if keys:
        for i in keys:
            vocab = SimpleVocabulary(
            [SimpleTerm(value=id, title=accounts[id]['name']) for id in keys])
    else:
        vocab = SimpleVocabulary.fromValues(keys)

    return vocab


alsoProvides(FacebookAccounts, IContextSourceBinder)

class IFacebookWallPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(title=_(u'Header'),
                                    description=_(u"The header for the portlet. Leave empty for none."),
                                    required=False)

    fb_account = schema.Choice(title=_(u'Facebook account'),
                               description=_(u"Which Facebook account to use."),
                               required=True,
                               source=FacebookAccounts)

    wall_id = schema.TextLine(title=_(u'Wall ID'),
                              description=_(u"ID for the wall you are trying "
                                             "to fetch from. More info in: "
                                             "https://developers.facebook.com/"
                                             "docs/reference/api/"),
                              required=True)

    max_results =  schema.Int(title=_(u'Maximum results'),
                               description=_(u"The maximum results number."),
                               required=True,
                               default=20)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IFacebookWallPortlet)

    header = u""
    fb_account = u""
    wall_id = u""
    max_results = 20
    
    def __init__(self,
                 fb_account,
                 wall_id,
                 max_results,
                 header=u""):
                     
        self.header = header
        self.fb_account = fb_account
        self.wall_id = wall_id
        self.max_results = max_results

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Facebook wall Portlet")



class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    
    render = ViewPageTemplateFile('fbwall.pt')


    def getHeader(self):
        """
        Returns the header for the portlet
        """
        return self.data.header

    def getSearchResults(self):
        registry = getUtility(IRegistry)
        accounts = registry['collective.facebook.accounts']

        result = None
        if self.data.fb_account in accounts:
            access_token = accounts[self.data.fb_account]['access_token']

            wall = self.data.wall_id + '/feed'
            params = access_token + '&limit=%s' % self.data.max_results
            url = GRAPH_URL % (wall, params)

            result = json.load(urllib.urlopen(url))

        return result

    def getFacebookLink(self):
                    
        return "https://www.facebook.com/%s" % self.data.wall_id

    def getDate(self, str_date):
        # Returns human readable date for the tweet
        date = DateTime.DateTime(str_date)

        return date
        
class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IFacebookWallPortlet)

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IFacebookWallPortlet)
