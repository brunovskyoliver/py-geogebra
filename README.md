# TODOS
- dynamicky scaling ui
- spravim auto update integrovany so serverom
- vytvorit pre kocyho nech vie compilovat kod


# HOW DOES IT WORK
- logiku prekladania som ukradol z odoo implementacie co som robil pre firmu
- vsetko co chceme mat prelozene do viacerych jazykov das cez ``_("epicky text")`` a potom ``./gen_translation.sh`` v terminali pregeneruje ``./locales/en/LC_MESSAGES/messages.po a ./locales/sk/LC_MESSAGES/messages.po``, tam editnes preklady a spustis ``./compile_translation.sh``
- nasledne mame classu ``Widgets``, do ktorej vieme pridavat widgety, ktore sa vytvaraju tkinterskou kniznicou a refreshnut ich text all in one
