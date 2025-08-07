import discord

def convert_attachments(attachments: list[discord.Attachment]) -> str:
    '''converts attachments into text at the end of the message linking to the attachments'''
    if not attachments: return ''
    images = []
    files = []
    for attachment in attachments:
        if attachment.content_type.startswith('image/'):
            images.append(attachment.url)
        else:
            files.append(attachment.url)
    result = ''
    if files:
        result += '\n' + ' '.join(files)
    if images:
        result += ' ' + ' '.join(f'[\u2800]({url})' for url in images)
        # unicode 2800 = BRAILLE PATTERN BLANK, blank character hides url
    return result