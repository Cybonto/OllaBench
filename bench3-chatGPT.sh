#! /usr/bin/env bash
# BENCH _3 - Tree of Thought Prompting - chatGPT
# Compare multiple models by asking them with the same questions

# defaults
declare -a SUMS=()

# Get flags
while getopts i:o:t:h flag
do
    case "${flag}" in
        i)  INPUT=${OPTARG};;
        o)  OUTPUT=${OPTARG};;
        t)  TARGET=${OPTARG};;
        h) 
            show_help;
            exit 1;;
    esac
done

# Check for empty variables
if [ -z "${INPUT}" ]; then
    echo "Input is not set. Exiting" 1>&2
    exit 1
fi
if [ -z "$OUTPUT" ]; then
    OUTPUT="bench_2_output.txt"
fi
if [ -z "$TARGET" ]; then
    # underdevelop
    TARGET="all"
fi

SUM_OUTPUT="sum_$OUTPUT"
printf "" > "$OUTPUT"

# Get the list of scenarios
while IFS="|" read -r SCENARIO DOMAIN ROLE CONTEXT QUESTION REFERENCE SENTENCE_PREF SENTENCE_MAX CONSTRAINT
do
    arr_SCENARIO+=("$SCENARIO")
    arr_DOMAIN+=("$DOMAIN")
    arr_ROLE+=("$ROLE")
    arr_CONTEXT+=("$CONTEXT")
    arr_QUESTION+=("$QUESTION")
    arr_REFERENCE+=("$REFERENCE")
    arr_SENTENCE_PREF+=("$SENTENCE_PREF")
    arr_SENTENCE_MAX+=("$SENTENCE_MAX")
    arr_CONSTRAINT+=("$CONSTRAINT")
done < <(tail -n +2 $INPUT)

printf "Scenario||Model||Answer||Note1||Note2\n" >> "$OUTPUT"

exec 5>&1

for i in "${!arr_QUESTION[@]}"; do
    echo " "
    echo "Model: chatGPT"
    echo "Scenario: ${arr_SCENARIO[$i]}"
    QUESTION="You are ${arr_ROLE[$i]}. ${arr_CONTEXT[$i]} ${arr_QUESTION[$i]} Let's first understand the problem. Describe the main problem in one sentence. In lesss than ${arr_SENTENCE_PREF[$i]} sentences, describe the potential cybersecurity risks and/or threats. In lesss than ${arr_SENTENCE_PREF[$i]} sentences, describe the best cybersecurity practices that might come from ${arr_REFERENCE[$i]} and might be used to solve the problem. Devise a plan to solve the problem in less than ${arr_SENTENCE_MAX[$i]} sentences, and with ${arr_CONSTRAINT[$i]}."
    echo "Answer: "
    QUESTION=`sed -e 's/^"//' -e 's/"$//' <<<"$QUESTION"`
    #echo "$QUESTION"
    ANSWER=$(gpt --no_markdown --prompt "$QUESTION" 2>&1 |tee /dev/fd/5)
    COMMAND_OUTPUT="${arr_SCENARIO[$i]}||chatGPT||$ANSWER||$SUM\n"
    printf "$COMMAND_OUTPUT" >> "$OUTPUT"
    # control for rate limit
    sleep 7
    printf "\n------"
done
