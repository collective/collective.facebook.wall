from Products.CMFCore.utils import getToolByName

def install(portal, reinstall=False):
    setup_tool = getToolByName(portal, 'portal_setup')
    if not reinstall:
        setup_tool.runAllImportStepsFromProfile('profile-collective.facebook.wall:initial')

    setup_tool.runAllImportStepsFromProfile('profile-collective.facebook.wall:default')
    return "Ran all uninstall steps."
    
def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile('profile-collective.facebook.wall:uninstall')
        return "Ran all uninstall steps."