"""How every letter, reminder and post is signed (owner, 20 Nov 2026: «подписывай zhol team, сделай опцию изменения и
его ввод… изменения имени имеется ввиду»).

The generators write this line; the send console (outreach/console/template.html, sign()) puts the sender's own
signature in its place when one is typed under «Подпись в письмах · изменить», and an empty field means this one.
The professors' letters (scripts/professor_letters.py) went out before and keep the name they were sent with.
"""
SIGN = "zhol team"
