import os
import glob
import re

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We want to replace await update.message.reply_text(..., parse_mode="Markdown")
    # with a safe try-except block, but it's easier to just strip problematic Markdown from the AI context.
    # Actually, a better way is to replace parse_mode="Markdown" with parse_mode=None for AI text,
    # OR catch the telegram.error.BadRequest.
    
    # Since writing a perfect AST transformer is hard, let's just add a helper function
    # at the top of each handler and replace update.message.reply_text with safe_reply.

    helper = """
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
    
    if "async def safe_reply" not in content:
        # Insert after imports
        imports_end = content.rfind("import")
        if imports_end != -1:
            line_end = content.find("\n", imports_end)
            content = content[:line_end+1] + helper + content[line_end+1:]

    # Replace update.message.reply_text with safe_reply(update, ...)
    # This regex handles basic cases.
    content = re.sub(r'await\s+update\.message\.reply_text\(\s*([^,]+)(,\s*parse_mode="Markdown")?\s*\)', 
                     r'await safe_reply(update, \1\2)', content)

    # Some multiline reply_text might exist
    content = content.replace("await update.message.reply_text(", "await safe_reply(update, ")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

handlers_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "handlers")
for pyfile in glob.glob(os.path.join(handlers_dir, "*.py")):
    if not pyfile.endswith("__init__.py"):
        patch_file(pyfile)
        print(f"Patched {pyfile}")
