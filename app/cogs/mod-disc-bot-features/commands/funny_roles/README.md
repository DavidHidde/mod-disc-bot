# Funny roles

Tired of creating roles for your guild members which are just their to be funny? This cog solves it by allowing users in
your guild to create the roles themselves.

The idea is simple: guild members can use the command `/give_role <user> <role_name>` to give other users a role and
use `/remove_role <user> <role>` to remove a role they have given to someone else. `/role_credit` can be used to check
which roles you have already given. Parameters include how many roles you can give out and which roles can't be given
out.

## Installation

The `mysql` extension is needed for this cog to persist a role database. If this extension is not yet enabled, a reload
is required for this cog to work.
