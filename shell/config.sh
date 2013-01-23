# Ad-hoc wrapper command for `factlog record'.
# Usage:
#    _factlog_record_wrapper COMMAND FILE [OPTIONS]
# Note that this wrapper does not work if the first option is not the
# file to open.  Supporting all possible option will require more
# dedicated handling than this.
_factlog_record_wrapper(){
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

alias less="_factlog_record_wrapper \\less"
alias vim="_factlog_record_wrapper \\vim"
