import sys
import io

from subprocess import getoutput as run
import traceback

from Barath import barath
from config import OWNER_ID, HANDLER 
from pyrogram import filters, enums
from pyrogram.errors import MessageTooLong



async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)




@barath.on_message(filters.user(OWNER_ID) & filters.command("logs",prefixes=HANDLER))
async def logs(_, message):
       run_logs = run("tail logs.txt")
       msg = await message.edit_text("Analyzing Logging...")
       thumb_id = "./Barath/barath_img/IMG_20230503_093609_915.jpg"
       with io.BytesIO(str.encode(run_logs)) as logs:
            logs.name = "logs.txt"
            await message.reply_document(
                document=logs, thumb=thumb_id
            )
       return await msg.delete()


@barath.on_message(filters.user(OWNER_ID) & filters.command("sh",prefixes=HANDLER))
async def sh(_, message):

    await message.edit("Analyzing Code...")
    
    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message

    try:
        code = message.text.split(message.text.split()[0])[1]
    except:
        return await message.edit("can you input the code to run my program?")

    x = run(code)

    try:

       await reply_to_.reply_text(f"**🖥️ Code**: ```{code}```\n\n**📝 Results**:\n```{x}```")
       return await message.delete()

    except MessageTooLong:
         with io.BytesIO(str.encode(run_logs)) as logs:
               logs.name = "shell.txt"

               await reply_to_.reply_document(
                   document=logs, thumb=thumb_id)

               return await message.delete()

    
@barath.on_message(filters.user(OWNER_ID) & filters.command("e",prefixes=HANDLER))
async def eval(client, message):

    msg = await message.edit_text("Analyzing Code...")

    try:
        cmd = message.text.split(message.text.split()[0])[1]
    except:
         return await msg.edit("can you input the code to run my program?")

    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success ✅"

    final_output = "<b>🖥️ Code</b>: "
    final_output += f"<code>{cmd}</code>\n\n"
    final_output += "<b>📝 Results</b>:\n"
    final_output += f"<code>{evaluation.strip()}</code>\n"

    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.txt"
            await reply_to_.reply_document(
                document=out_file, caption=f'<code>{cmd}</code>', parse_mode=enums.ParseMode.HTML)
            return await message.delete()
    else:
        await reply_to_.reply_text(final_output, parse_mode=enums.ParseMode.HTML)
        return await message.delete()
