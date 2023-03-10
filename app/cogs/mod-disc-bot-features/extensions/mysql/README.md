# MySQL Connector

This extension provides a static MySQL connector class that can be used for interacting with a database.
The `mysql-python-connector` is used for this purpose.

## Installation

The `docker/mysql-template.env` file shows an example of a database configuration. Use this to make your own `mysql.env`
file which Docker will use to launch your MySQL database. Note that enabling this cog requires a reboot.

## Example

```python
def get_required_extensions(self) -> list[str]:
    """Get a list of extensions that are required to run this cog"""
    return [
        'mysql',
        ...
    ]


@app_commands.command()
async def some_command(self, ctx: discord.Interaction):
    cursor = self._bot.get_cog('mysql').cursor
    cursor.execute(
        """
            SOME SQL QUERY
        """
    )
    cursor.commit()
    return await ctx.response.send_message(content='Executed some DB call')
```