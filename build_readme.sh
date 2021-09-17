#!/bin/bash

function get_init_key {
    value=$(grep __$1__ src/__init__.py)
    if [ $? ]; then
        echo ${value##*=} | tr -d '"' | tr -d "'"
    else
        echo "$1"
    fi
}

function toc {
    FILE=${1:?No file was specified as first argument}

    declare -a TOC
    CODE_BLOCK=0
    CODE_BLOCK_REGEX='^```'
    HEADING_REGEX='^#{1,}'

    while read -r LINE; do
        # Treat code blocks
        if [[ "${LINE}" =~ $CODE_BLOCK_REGEX ]]; then
            # Ignore things until we see code block ending
            CODE_BLOCK=$((CODE_BLOCK + 1))
            if [[ "${CODE_BLOCK}" -eq 2 ]]; then
                # We hit the closing code block
                CODE_BLOCK=0
            fi
            continue
        fi

        # Treat normal line
        if [[ "${CODE_BLOCK}" == 0 ]]; then
            # If we see heading, we save it to ToC map
            if [[ "${LINE}" =~ ${HEADING_REGEX} ]]; then
                TOC+=("${LINE}")
            fi
        fi
    done < <(grep -v '## Table of Contents' "${FILE}")

    echo -e "## Table of Contents\n"
    for LINE in "${TOC[@]}"; do
        case "${LINE}" in
        '#####'*)
            echo -n "        - "
            ;;
        '####'*)
            echo -n "      - "
            ;;
        '###'*)
            echo -n "    - "
            ;;
        '##'*)
            echo -n "  - "
            ;;
        '#'*)
            echo -n "- "
            ;;
        esac

        LINK=${LINE}
        # Detect markdown links in heading and remove link part from them
        if grep -qE "\[.*\]\(.*\)" <<<"${LINK}"; then
            LINK=$(sed 's/\(\]\)\((.*)\)/\1/' <<<"${LINK}")
        fi
        # Special characters (besides '-') in page links in markdown
        # are deleted and spaces are converted to dashes
        LINK=$(tr -dc "[:alnum:] _-" <<<"${LINK}")
        LINK=${LINK/ /}
        LINK=${LINK// /-}
        LINK=${LINK,,}
        LINK=$(tr -s "-" <<<"${LINK}")

        # Print in format [Very Special Heading](#very-special-heading)
        echo "[${LINE#\#* }](#${LINK})"
    done
}
README="README.md"
echo "Generating $README"

cp docs/template.md $README

for key in "description" "version" "author" "author_email" "package_name" "tool_name"; do
    value=$(get_init_key $key)
    awk "{sub(\"_${key}_\",\"$value\")}1" $README >docs/template.tmp0 && mv docs/template.tmp0 $README
    echo "+- Template var: $key=$value"
done
tool_name=$value

echo "+- Generating help"
echo '``` bash' >>help.txt
echo "\$ $tool_name --help" >>help.txt
python3 run.py -h >>help.txt
echo '```' >>help.txt
echo "" >>help.txt

options_re="\{(.*)\}"
for line in $(python run.py --help | grep '\{.*\}'); do
    if [[ $line =~ $options_re ]]; then
        options="${BASH_REMATCH[1]}"
    fi
done

options="${options//,/ }"
for option in $options; do
    echo "  +- help $option"
    echo "### ${option^^}" >>help.txt
    echo "" >>help.txt
    echo '``` bash' >>help.txt
    echo "\$ $tool_name $option --help" >>help.txt
    python3 run.py $option -h >>help.txt
    echo '```' >>help.txt
    echo "" >>help.txt
done

awk 'NR==FNR { a[n++]=$0; next} /_help_/ { for (i=0;i<n;++i) print a[i]; next }1' help.txt $README >docs/template.tmp0 && mv docs/template.tmp0 $README
rm help.txt

echo "+- Table of contents"
toc $README >toc.txt

awk 'NR==FNR { a[n++]=$0; next} /_toc_/ { for (i=0;i<n;++i) print a[i]; next }1' toc.txt $README >docs/template.tmp0 && mv docs/template.tmp0 $README
rm toc.txt

echo "--- DONE"
