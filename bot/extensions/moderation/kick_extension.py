from matrix import Context, Extension
from matrix.errors import CheckError

from bot.permissions import is_moderator
from .kick_service import kick_from_context
from .models import KickResult
from .errors import SpaceNotFoundError

extension = Extension("kick")

KICK_RESULT_TEMPLATE = (
    "{space}"
    "Target: `{target}`\n"
    "Kicked from: `{kicked}` rooms\n"
    "Failed in: `{failed}` rooms\n"
    "Reason: {reason}"
)


def format_kick_result(result: KickResult) -> str:
    return KICK_RESULT_TEMPLATE.format(
        space=f"Space: `{result.space_id}`\n" if result.space_id else "",
        target=result.target_user_id,
        kicked=len(result.kicked_room_ids),
        failed=len(result.failed_room_ids),
        reason=result.reason,
    )


@extension.command(
    "kick",
    description="Kick a user from all rooms in the current space",
)
async def kick(
    ctx: Context,
    user_id: str,
    reason: str = "No reason provided",
) -> None:
    result = await kick_from_context(ctx, user_id, reason)
    await ctx.reply(format_kick_result(result))


@kick.error(SpaceNotFoundError)
async def kick_space_error(ctx: Context, error: SpaceNotFoundError) -> None:
    await ctx.reply(f"Could not complete kick operation: {error}")


@kick.error(CheckError)
async def kick_check_error(ctx: Context, error: CheckError) -> None:
    await ctx.reply(f"Could not complete kick operation: {error}")


@kick.check
async def can_kick(ctx: Context) -> bool:
    return await is_moderator(ctx)
