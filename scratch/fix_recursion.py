import os
import glob

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The buggy string is:
    # async def safe_reply(update, text, **kwargs):
    #     try:
    #         await safe_reply(update, text, **kwargs)
    #     except BadRequest as e:
    #         if "parse entities" in str(e).lower():
    #             # Fallback without markdown
    #             kwargs.pop("parse_mode", None)
    #             await safe_reply(update, text, **kwargs)
    
    # We want to replace the inner safe_reply calls back to update.message.reply_text
    
    correct_helper = """
from telegram.error import BadRequest
async def safe_reply(update, text, **kwargs):
    try:
        await update.message.reply_text(text, **kwargs)
    except BadRequest as e:
        if "parse entities" in str(e).lower():
            # Fallback without markdown
            kwargs.pop("parse_mode", None)
            await update.message.reply_text(text, **kwargs)
        else:
            raise e
"""
    
    # We can just extract the buggy block and replace it.
    start_idx = content.find("from telegram.error import BadRequest")
    if start_idx != -1:
        end_idx = content.find("        else:\n            raise e\n")
        if end_idx != -1:
            end_idx += len("        else:\n            raise e\n")
            content = content[:start_idx] + correct_helper.strip() + "\n" + content[end_idx:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

handlers_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "handlers")
for pyfile in glob.glob(os.path.join(handlers_dir, "*.py")):
    if not pyfile.endswith("__init__.py"):
        fix_file(pyfile)
        print(f"Fixed {pyfile}")
