#!/usr/bin/env python3
"""
Known sources for 3ds Max INI parameters
Curated list of reliable documentation and discussions
"""

# Official Autodesk Documentation
AUTODESK_DOCS = [
    {
        'url': 'https://help.autodesk.com/cloudhelp/2026/ENU/3DSMax-Basics/files/GUID-AFC5FE94-8B39-4AB9-99DC-DF7AF309BF2A.htm',
        'title': 'The Initialization File',
        'type': 'official',
        'priority': 10
    },
    {
        'url': 'https://help.autodesk.com/cloudhelp/2023/ENU/3DSMax-Customizing/files/GUID-C9DAE600-D8D2-4AE5-85E4-6386195263A2.htm',
        'title': '3rd Party Plug-Ins Path Configuration',
        'type': 'official',
        'priority': 9
    },
]

# Forums (Community discussions)
FORUM_THREADS = [
    {
        'url': 'https://forums.autodesk.com/t5/3ds-max-programming-forum/changing-ini-settings-post-system-shutdown/td-p/13257182',
        'title': 'Changing INI settings post system shutdown',
        'type': 'forum',
        'priority': 8
    },
    {
        'url': 'https://forums.autodesk.com/t5/3ds-max-forum/3ds2020-3dsmax-ini/td-p/8701087',
        'title': '3ds2020 - 3dsmax.ini',
        'type': 'forum',
        'priority': 7
    },
    {
        'url': 'https://forums.autodesk.com/t5/3ds-max-programming-forum/3ds-max-2024-ini-file-read-write-error/td-p/12548867',
        'title': '3ds max 2024 .ini file read/write error',
        'type': 'forum',
        'priority': 7
    },
    {
        'url': 'https://forums.autodesk.com/t5/3ds-max-forum/3dsmax-ini-reference-guide/td-p/8406159',
        'title': '3dsmax.ini reference guide',
        'type': 'forum',
        'priority': 9
    },
]

# Community Blogs & Resources
COMMUNITY_RESOURCES = [
    {
        'url': 'https://www.designimage.co.uk/how-to-quickly-locate-those-pesky-3dsmax-settings-and-folders/',
        'title': 'How to quickly locate 3dsmax settings',
        'type': 'blog',
        'priority': 6
    },
    {
        'url': 'https://www.designimage.co.uk/backup-and-restore-3dsmax-settings/',
        'title': 'Backup and restore 3dsMax.ini settings',
        'type': 'blog',
        'priority': 6
    },
]

# GitHub Examples
GITHUB_EXAMPLES = [
    {
        'url': 'https://github.com/Alhadis/3DSMax-Setup/blob/master/ENU/Plugin.UserSettings.ini',
        'title': '3DSMax-Setup Plugin.UserSettings.ini',
        'type': 'github',
        'priority': 5
    },
]

# Plugin Documentation
PLUGIN_DOCS = [
    {
        'url': 'https://corona-renderer.com/doc',
        'title': 'Corona Renderer Documentation',
        'type': 'plugin_official',
        'priority': 9
    },
    {
        'url': 'https://support.chaos.com/hc/en-us/articles/4528599396881-Corona-Converter-script-is-not-working',
        'title': 'Corona Converter INI location',
        'type': 'plugin_official',
        'priority': 8
    },
    {
        'url': 'https://docs.itoosoft.com/installation/forest-pack-installation-files',
        'title': 'Forest Pack Installation & Files',
        'type': 'plugin_official',
        'priority': 9
    },
]

# Plugin-specific forums
PLUGIN_FORUMS = [
    {
        'url': 'https://forum.itoosoft.com/forest-pro-%28%2A%29/custom-paths/',
        'title': 'iToo Forest Pro - Custom paths',
        'type': 'plugin_forum',
        'priority': 6
    },
    {
        'url': 'https://forum.itoosoft.com/forest-pro-%28%2A%29/issues-with-network-paths-registry-edits-ini-files/',
        'title': 'iToo - Issues with network paths, registry, ini files',
        'type': 'plugin_forum',
        'priority': 7
    },
    {
        'url': 'https://forum.itoosoft.com/forest-pro-%28%2A%29/library-paths-question/',
        'title': 'iToo - Library paths question',
        'type': 'plugin_forum',
        'priority': 6
    },
    {
        'url': 'https://forum.chaos.com/categories/v-ray-for-3ds-max',
        'title': 'Chaos Group Forum - V-Ray for 3ds Max',
        'type': 'plugin_forum',
        'priority': 7
    },
]

# Community Forums & Blogs
COMMUNITY_FORUMS = [
    {
        'url': 'https://www.scriptspot.com/forums/3ds-max/general-scripting/',
        'title': 'ScriptSpot - MaxScript & Tools',
        'type': 'community',
        'priority': 8
    },
    {
        'url': 'https://cgsociety.org/forums/3ds-max-',
        'title': 'CGTalk / CGSociety - 3ds Max',
        'type': 'community',
        'priority': 7
    },
    {
        'url': 'https://polycount.com/discussion/',
        'title': 'Polycount - 3ds Max discussions',
        'type': 'community',
        'priority': 7
    },
]

def get_all_sources():
    """Get all sources sorted by priority"""
    all_sources = (
        AUTODESK_DOCS + 
        FORUM_THREADS + 
        COMMUNITY_RESOURCES + 
        GITHUB_EXAMPLES + 
        PLUGIN_DOCS +
        PLUGIN_FORUMS +
        COMMUNITY_FORUMS
    )
    return sorted(all_sources, key=lambda x: -x['priority'])

def get_sources_by_type(source_type: str):
    """Get sources by type"""
    all_sources = get_all_sources()
    return [s for s in all_sources if s['type'] == source_type]

