cd resources/icons
for f in *-[0-9]*.png; do
    mv "$f" "${f/-[0-9]*/.png}"
done
