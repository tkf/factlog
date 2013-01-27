# Ad-hoc wrapper command for `factlog record'.
# Usage:
#    factlog-record-wrapper COMMAND FILE [OPTIONS]
# Examples:
#    alias less="factlog-record-wrapper \\less"
#    alias vim="factlog-record-wrapper \\vim"
# Note that this wrapper does not work if the first option is not the
# file to open.  Supporting all possible option will require more
# dedicated handling than this.
factlog-record-wrapper(){
    local command="$1"
    local file="$2"
    local code
    if [ "$#" = 1 ]
    then
        "$command"
        code="$?"
        return $code
    fi
    shift 2
    if [ -e "$file" ]
    then
        factlog record -a open "$file"
        "$command" "$file" "$@"
        code="$?"
        factlog record -a close "$file"
        return $code
    else
        "$command" "$file" "$@"
    fi
}
