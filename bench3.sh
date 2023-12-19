#! /usr/bin/env bash
# BENCH _2 - Plan and Solve Prompting
# Compare multiple models by asking them with the same questions

# defaults
declare -a SUMS=()
declare -a MODELS=()

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

# Get the list of models
MODELS=($(ollama list | awk '{print $1}' | tail -n +2 ))
#MODELS=(Llama Orca)

printf "Scenario||Model||Answer||Total Duration(s)||Load Duration(ms)||Prompt Eval Count(tokens)||Prompt Eval Duration(s)||Prompt Eval Rate(tokens/s)||Eval Count(tokens)||Eval Duration(s)||Eval Rate(tokens/s)||Note1||Note2\n" >> "$OUTPUT"

# Loop through each of the selected models
for ITEM in "${MODELS[@]}"; do
    echo "--------------------------------------------------------------"
    echo "Loading model $ITEM"
    ollama run "$ITEM" ""
    ollama run "$ITEM" ""
    ollama run "$ITEM" "" #attempt to load the same model 3 times just in case big models fail to load
    echo "--------------------------------------------------------------"
    echo "Running the questions through the model $ITEM"
    exec 5>&1

    for i in "${!arr_QUESTION[@]}"; do
      echo " "
      echo "Model: ${ITEM}"
      echo "Scenario: ${arr_SCENARIO[$i]}"
      QUESTION="You are ${arr_ROLE[$i]}. ${arr_CONTEXT[$i]} ${arr_QUESTION[$i]} Let's first understand the problem. Describe the main problem in one sentence. In lesss than ${arr_SENTENCE_PREF[$i]} sentences, describe the potential cybersecurity risks and/or threats. In lesss than ${arr_SENTENCE_PREF[$i]} sentences, describe the best cybersecurity practices that might come from ${arr_REFERENCE[$i]} and might be used to solve the problem. Devise a plan to solve the problem in less than ${arr_SENTENCE_MAX[$i]} sentences, and with ${arr_CONSTRAINT[$i]}."
      echo "Answer: "
      QUESTION=`sed -e 's/^"//' -e 's/"$//' <<<"$QUESTION"`
      #echo "$QUESTION"
      ANSWER=$(ollama run "$ITEM" "$QUESTION" --verbose 2>&1 |tee /dev/fd/5)
      SUM=$(echo "$ANSWER" | awk '
        /eval duration:/ {
            value = $3
            if (index(value, "ms") > 0) {
                gsub("ms", "", value)
                value /= 1000
            } else {
                gsub("s", "", value)
            }
            sum += value
        }
        END { print sum }')
      temp_ANSWER=$(echo "$ANSWER"|grep "\S"|sed ':a;N;$!ba;s/\n/ /g'|awk -F 'total duration:' '{print $1}'|sed 's/\[?\(;*[0-9][0-9]*\)*[fhlmpsuABCDEFGHJKST]//g'|sed 's/[\x01-\x1F]//g')
      temp_METRICS=$(echo "$ANSWER"|awk -F ':' '{print $2}'|grep "\S"|sed 's/.*/\U&||/'|sed ':a;N;$!ba;s/\n/ /g')
      #echo "test: $temp_ANSWER"
      ANSWER=$(echo "$temp_ANSWER||$temp_METRICS"|tr -dc '[:print:]\n\r'| tr -s ' '|sed 's/\[[^]]*\[1G//g'|sed 's/\[[^]]*\[25H//g')
      COMMAND_OUTPUT="${arr_SCENARIO[$i]}||${ITEM}||$ANSWER||$SUM\n"
      printf "$COMMAND_OUTPUT" >> "$OUTPUT"
      echo "------"
    done
done