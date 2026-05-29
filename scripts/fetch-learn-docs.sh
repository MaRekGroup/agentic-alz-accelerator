#!/usr/bin/env bash
set -euo pipefail

# fetch-learn-docs.sh — Query Microsoft Learn MCP server for Azure documentation
# Usage:
#   ./scripts/fetch-learn-docs.sh search "Azure Firewall best practices"
#   ./scripts/fetch-learn-docs.sh fetch "https://learn.microsoft.com/azure/firewall/overview"
#   ./scripts/fetch-learn-docs.sh code "Azure Firewall Bicep deployment" bicep

MCP_ENDPOINT="https://learn.microsoft.com/api/mcp"
ACCEPT_HEADER="Accept: application/json, text/event-stream"
CONTENT_TYPE="Content-Type: application/json"

usage() {
    echo "Usage: $0 <command> <query> [language]"
    echo ""
    echo "Commands:"
    echo "  search <query>              Search Microsoft Learn documentation"
    echo "  fetch <url>                 Fetch full page content by URL"
    echo "  code <query> [language]     Search for code samples (optional: bicep, terraform, powershell, etc.)"
    echo ""
    echo "Examples:"
    echo "  $0 search 'Azure Firewall premium features'"
    echo "  $0 fetch 'https://learn.microsoft.com/azure/firewall/overview'"
    echo "  $0 code 'deploy Azure Firewall' bicep"
    exit 1
}

parse_sse_response() {
    # SSE format: "event: message\ndata: {json}\n"
    # Extract the JSON from the data line
    grep -o '^data: .*' | sed 's/^data: //'
}

cmd_search() {
    local query="$1"
    local payload
    payload=$(cat <<EOF
{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "microsoft_docs_search",
        "arguments": {"query": "$query"}
    },
    "id": 1
}
EOF
)
    local response
    response=$(curl -s -X POST "$MCP_ENDPOINT" \
        -H "$CONTENT_TYPE" \
        -H "$ACCEPT_HEADER" \
        -d "$payload")

    # Parse SSE response
    echo "$response" | parse_sse_response | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    content = data.get('result', {}).get('content', [])
    for item in content:
        if item.get('type') == 'text':
            text_data = json.loads(item['text'])
            results = text_data if isinstance(text_data, list) else text_data.get('results', [])
            for r in results:
                title = r.get('title', 'No title')
                url = r.get('contentUrl', r.get('url', 'No URL'))
                content_text = r.get('content', '')
                print(f'## {title}')
                print(f'URL: {url}')
                if content_text:
                    print(f'{content_text[:500]}')
                print()
except Exception as e:
    print(f'Error parsing response: {e}', file=sys.stderr)
    print(sys.stdin.read() if hasattr(sys.stdin, 'read') else '', file=sys.stderr)
" 2>/dev/null || echo "$response" | parse_sse_response
}

cmd_fetch() {
    local url="$1"
    local payload
    payload=$(cat <<EOF
{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "microsoft_docs_fetch",
        "arguments": {"url": "$url"}
    },
    "id": 1
}
EOF
)
    local response
    response=$(curl -s -X POST "$MCP_ENDPOINT" \
        -H "$CONTENT_TYPE" \
        -H "$ACCEPT_HEADER" \
        -d "$payload")

    echo "$response" | parse_sse_response | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    content = data.get('result', {}).get('content', [])
    for item in content:
        if item.get('type') == 'text':
            print(item['text'])
except Exception as e:
    print(f'Error parsing response: {e}', file=sys.stderr)
" 2>/dev/null || echo "$response" | parse_sse_response
}

cmd_code() {
    local query="$1"
    local language="${2:-}"
    local args
    if [[ -n "$language" ]]; then
        args="{\"query\": \"$query\", \"language\": \"$language\"}"
    else
        args="{\"query\": \"$query\"}"
    fi
    local payload
    payload=$(cat <<EOF
{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "microsoft_code_sample_search",
        "arguments": $args
    },
    "id": 1
}
EOF
)
    local response
    response=$(curl -s -X POST "$MCP_ENDPOINT" \
        -H "$CONTENT_TYPE" \
        -H "$ACCEPT_HEADER" \
        -d "$payload")

    echo "$response" | parse_sse_response | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    content = data.get('result', {}).get('content', [])
    for item in content:
        if item.get('type') == 'text':
            text_data = json.loads(item['text'])
            results = text_data if isinstance(text_data, list) else text_data.get('results', [])
            for r in results:
                desc = r.get('description', 'No description')
                link = r.get('link', 'No link')
                lang = r.get('language', 'unknown')
                snippet = r.get('codeSnippet', '')
                print(f'## {desc}')
                print(f'Language: {lang} | URL: {link}')
                if snippet:
                    print(f'\`\`\`{lang}')
                    print(snippet[:1000])
                    print('\`\`\`')
                print()
except Exception as e:
    print(f'Error parsing response: {e}', file=sys.stderr)
" 2>/dev/null || echo "$response" | parse_sse_response
}

# Main
if [[ $# -lt 2 ]]; then
    usage
fi

command="$1"
shift

case "$command" in
    search)
        cmd_search "$1"
        ;;
    fetch)
        cmd_fetch "$1"
        ;;
    code)
        cmd_code "$1" "${2:-}"
        ;;
    *)
        echo "Unknown command: $command"
        usage
        ;;
esac
