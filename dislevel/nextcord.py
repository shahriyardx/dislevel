from ._cog import Leveling


def setup(bot):
    bot.add_cog(Leveling(bot))
