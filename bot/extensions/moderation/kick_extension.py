from matrix import Context, Extension
from matrix.errors import MatrixError

from .kick_service import kick_from_context
from .models import KickResult

extension = Extension("kick")


def format_kick_result(result: KickResult) -> str:
    if result.space_id is None:
        return "\n".join(
            [
                f"Target: `{result.target_user_id}`",
                f"Reason: {result.reason}",
            ]
        )

    lines = [
        f"Space: `{result.space_id}`",
        f"Target: `{result.target_user_id}`",
        f"Kicked from: `{len(result.kicked_room_ids)}` rooms",
        f"Reason: {result.reason}",
    ]

    return "\n".join(lines)


@extension.command(
    "kick",
    description="Kick a user from all rooms in the current space",
)
async def kick(
    ctx: Context,
    user_id: str,
    reason: str = "No reason provided",
) -> None:
    try:
        result = await kick_from_context(ctx, user_id, reason)
    except MatrixError as e:
        await ctx.reply(f"Could not complete kick operation: {e}")
        return

    await ctx.reply(format_kick_result(result))
