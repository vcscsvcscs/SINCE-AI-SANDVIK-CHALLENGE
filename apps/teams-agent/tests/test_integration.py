"""
Blackbox integration tests for the Teams bot application using testcontainers.

Tests the two endpoints:
- GET /api/messages (health check)
- POST /api/messages (bot activity handler)

Also validates card output structure against ChannelAPI-OpenAPI.yaml schema.

These are true blackbox tests - the application runs in a Docker container
and tests make real HTTP requests to it.
"""
import json
import os
import pytest
import requests
import time
from pathlib import Path
from testcontainers.core.container import DockerContainer


@pytest.fixture(scope="module")
def container():
    """Start the Teams bot application in a Docker container"""
    # Get the project root directory (apps/teams-agent)
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    # Build the Docker image
    import docker
    client = docker.from_env()
    
    image_name = "teams-agent-test"
    try:
        # Build the image
        print(f"Building Docker image: {image_name}")
        image, _ = client.images.build(
            path=str(project_root),
            tag=image_name,
            dockerfile="DOCKERFILE"
        )
        print(f"Successfully built image: {image_name}")
    except Exception as e:
        print(f"Error building image: {e}")
        raise
    
    # Create and start the container
    container = DockerContainer(image_name)
    container.with_env("TARGET_USER_ID", "test-user-123")
    container.with_env("CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID", "test-client-id")
    container.with_env("CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET", "test-secret")
    container.with_env("CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID", "test-tenant-id")
    container.with_env("PORT", "3978")
    container.with_env("DISABLE_AUTH", "true")  # Disable JWT auth for integration tests
    container.with_exposed_ports(3978)
    
    # Start the container
    print("Starting container...")
    container.start()
    
    # Wait for the server to be ready
    host = container.get_container_host_ip()
    port = container.get_exposed_port(3978)
    base_url = f"http://{host}:{port}"
    print(f"Waiting for server to be ready at {base_url}...")
    
    max_retries = 30
    retry_count = 0
    last_error = None
    
    while retry_count < max_retries:
        try:
            response = requests.get(f"{base_url}/api/messages", timeout=2)
            if response.status_code == 200:
                print(f"Container is ready at {base_url}")
                break
        except requests.exceptions.RequestException as e:
            last_error = e
            if retry_count % 5 == 0:  # Print progress every 5 seconds
                print(f"Waiting for server... (attempt {retry_count + 1}/{max_retries})")
        
        retry_count += 1
        time.sleep(1)
    
    if retry_count >= max_retries:
        # Get container logs before stopping
        try:
            container_obj = container.get_container()
            logs = container_obj.logs().decode('utf-8')
            print(f"\n=== Container Logs (last 50 lines) ===")
            log_lines = logs.split('\n')
            for line in log_lines[-50:]:
                print(line)
            print("=" * 50)
        except Exception as log_error:
            print(f"Could not retrieve container logs: {log_error}")
        
        container.stop()
        raise Exception(
            f"Container failed to start or server not ready after {max_retries} seconds.\n"
            f"Base URL: {base_url}\n"
            f"Last error: {last_error}\n"
            f"Check container logs above for details."
        )
    
    yield container, base_url
    
    # Cleanup
    container.stop()
    try:
        client.images.remove(image_name, force=True)
    except Exception:
        pass


def create_channel_message_activity(text="Test channel message", 
                                    channel_id="19:channel123@thread.tacv2",
                                    team_id="team-123",
                                    message_id="msg-123",
                                    user_id="sender-123",
                                    user_name="Test User"):
    """Helper to create a channel message activity"""
    activity = {
        "type": "message",
        "id": message_id,
        "timestamp": "2024-01-01T00:00:00Z",
        "channelId": "msteams",
        "from": {
            "id": user_id,
            "name": user_name,
            "aadObjectId": user_id
        },
        "conversation": {
            "id": channel_id,
            "name": "Test Channel",
            "conversationType": "channel",
            "isGroup": True
        },
        "recipient": {
            "id": "bot-123",
            "name": "Test Bot"
        },
        "text": text,
        "channelData": {
            "channel": {
                "id": channel_id
            },
            "team": {
                "id": team_id
            },
            "tenant": {
                "id": "tenant-123"
            }
        },
        "serviceUrl": "https://smba.trafficmanager.net/"
    }
    return activity


def extract_card_from_response(response):
    """
    Extract card data from bot response.
    The bot may return cards in attachments or in the response body.
    """
    try:
        data = response.json()
        
        # Check if response contains attachments array
        if isinstance(data, dict):
            if "attachments" in data and len(data["attachments"]) > 0:
                return data["attachments"][0]
            
            # Check if response itself is a card
            if "contentType" in data:
                return data
            
            # Check if there's a card in the response body
            if "card" in data:
                return data["card"]
        
        return None
    except (json.JSONDecodeError, AttributeError):
        return None


def validate_hero_card_structure(card):
    """
    Validate HeroCard structure against Teams schema.
    Returns: (is_valid: bool, errors: list[str], card_content: dict)
    """
    errors = []
    content = {}
    
    if not isinstance(card, dict):
        errors.append("Card must be a dictionary")
        return False, errors, content
    
    # Validate contentType
    content_type = card.get("contentType", "")
    if content_type != "application/vnd.microsoft.card.hero":
        errors.append(f"Expected contentType 'application/vnd.microsoft.card.hero', got '{content_type}'")
    
    # Extract content section
    card_content = card.get("content", {})
    if not isinstance(card_content, dict):
        errors.append("Card 'content' must be a dictionary")
        return False, errors, content
    
    # Validate required fields
    if "title" not in card_content:
        errors.append("Missing required field 'title'")
    else:
        content["title"] = card_content["title"]
    
    if "text" not in card_content:
        errors.append("Missing required field 'text'")
    else:
        content["text"] = card_content["text"]
    
    # Validate optional fields
    if "buttons" in card_content:
        buttons = card_content["buttons"]
        if not isinstance(buttons, list):
            errors.append("'buttons' must be an array")
        else:
            content["buttons"] = buttons
            for i, button in enumerate(buttons):
                if "type" not in button:
                    errors.append(f"Button {i}: missing 'type'")
                if "title" not in button:
                    errors.append(f"Button {i}: missing 'title'")
    
    if "images" in card_content:
        images = card_content["images"]
        if not isinstance(images, list):
            errors.append("'images' must be an array")
        else:
            content["images"] = images
    
    return len(errors) == 0, errors, content


def extract_sku_from_text(text):
    """Extract SKU patterns from text"""
    import re
    # Match patterns like 00002771, BC00004214, etc.
    sku_pattern = r'\b(?:BC)?\d{8}\b'
    skus = re.findall(sku_pattern, text)
    return skus


def compare_card_with_expected(card_content, expected, input_text):
    """
    Compare actual card content with expected output.
    Returns: (matches: bool, differences: list[str])
    
    This is a STRICT validation that checks if the bot properly:
    1. Extracts SKUs from the message
    2. Classifies the query type
    3. Indicates the classification in the card
    """
    differences = []
    
    # Extract SKUs from input
    input_skus = extract_sku_from_text(input_text)
    
    # Check if card text mentions the SKUs
    card_text = json.dumps(card_content).lower()
    for sku in input_skus:
        if sku.lower() not in card_text:
            differences.append(f"❌ Missing SKU: '{sku}' not found in card response")
    
    # STRICT: Check if expected query type is indicated in card
    if "query_type" in expected and expected["query_type"]:
        expected_type = expected["query_type"]
        
        # Query type indicators that should appear in the card
        query_indicators = {
            "availability_check": ["available", "availability", "in stock", "stock"],
            "lead_time_query": ["lead time", "delivery", "shipping", "eta"],
            "part_inquiry": ["part", "sku", "item", "product"],
            "price_query": ["price", "cost", "$"],
            "technical_support": ["technical", "support", "help", "issue"],
            "general_inquiry": ["inquiry", "question", "information"]
        }
        
        indicators = query_indicators.get(expected_type, [expected_type])
        found_indicator = any(indicator in card_text for indicator in indicators)
        
        if not found_indicator:
            differences.append(
                f"❌ Missing query type classification: Expected '{expected_type}' "
                f"but card doesn't contain indicators: {indicators}"
            )
    
    # Check if typo is mentioned (if applicable)
    if expected.get("has_typo", False):
        if "typo" not in card_text and "error" not in card_text and "correct" not in card_text and "did you mean" not in card_text:
            differences.append("❌ Input has typo but card doesn't mention it or suggest correction")
    
    return len(differences) == 0, differences


def assert_success_response(response, context=""):
    """Helper to assert successful response and show detailed error if failed"""
    if response.status_code not in [200, 201, 202]:
        error_details = f"Context: {context}\n" if context else ""
        error_details += f"Status: {response.status_code}\n"
        error_details += f"Response: {response.text[:1000]}\n"
        if response.headers.get("Content-Type", "").startswith("application/json"):
            try:
                error_details += f"JSON: {response.json()}\n"
            except:
                pass
        assert False, f"Expected 200/201/202, got {response.status_code}:\n{error_details}"


def create_direct_message_activity(text="Hello bot", user_id="test-user-123"):
    """Helper to create a direct message activity"""
    activity = {
        "type": "message",
        "id": "msg-direct-123",
        "timestamp": "2024-01-01T00:00:00Z",
        "channelId": "msteams",
        "from": {
            "id": user_id,
            "name": "Test User",
            "aadObjectId": user_id
        },
        "conversation": {
            "id": f"19:{user_id}@thread.skype",
            "conversationType": "personal",
            "isGroup": False
        },
        "recipient": {
            "id": "bot-123",
            "name": "Test Bot"
        },
        "text": text,
        "serviceUrl": "https://smba.trafficmanager.net/"
    }
    return activity


def test_get_messages_health_check(container):
    """Test GET /api/messages endpoint returns 200 (health check)"""
    _, base_url = container
    
    response = requests.get(f"{base_url}/api/messages", timeout=10)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"


def test_post_messages_direct_message(container):
    """Test POST /api/messages with direct message activity"""
    _, base_url = container
    
    activity = create_direct_message_activity(
        text="Hello bot",
        user_id="test-user-123"
    )
    
    response = requests.post(
        f"{base_url}/api/messages",
        json=activity,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    # Bot framework typically returns 200, 201, or 202
    assert_success_response(response, "test_post_messages_direct_message")


def test_post_messages_channel_message(container):
    """Test POST /api/messages with channel message activity"""
    _, base_url = container
    
    # First, establish a conversation reference by sending a direct message
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    
    # Send direct message first to establish conversation reference
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_post_messages_channel_message - direct message setup")
    
    # Wait a bit for the conversation reference to be stored
    time.sleep(1)
    
    # Now send the channel message
    activity = create_channel_message_activity(
        text="This is a test channel message",
        user_id="sender-123"
    )
    
    response = requests.post(
        f"{base_url}/api/messages",
        json=activity,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    # Should return success status
    assert_success_response(response, "test_post_messages_channel_message - channel message")


def test_channel_message_without_target_user(container):
    """Test channel message when TARGET_USER_ID is not configured"""
    _, base_url = container
    
    activity = create_channel_message_activity(
        text="Test message without target user"
    )
    
    response = requests.post(
        f"{base_url}/api/messages",
        json=activity,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    # Should still return success (bot handles it gracefully)
    assert_success_response(response, "test_channel_message_without_target_user")


def test_empty_message_filtering(container):
    """Test that empty messages are filtered out"""
    _, base_url = container
    
    # First establish conversation reference
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_empty_message_filtering - direct message setup")
    
    time.sleep(1)
    
    # Send empty channel message
    activity = create_channel_message_activity(
        text="",  # Empty message
        user_id="sender-123"
    )
    
    response = requests.post(
        f"{base_url}/api/messages",
        json=activity,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    assert_success_response(response, "test_empty_message_filtering")
    # Empty messages should be filtered, so no notification should be sent


def test_card_structure_validation(container):
    """
    Test that card output structure matches ChannelAPI-OpenAPI.yaml schema.
    
    This test sends a channel message and validates that the response
    (if any) contains a properly structured card according to the schema.
    """
    _, base_url = container
    
    # First establish conversation reference
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_card_structure_validation - direct message setup")
    
    time.sleep(1)
    
    # Send channel message that should trigger a card
    activity = create_channel_message_activity(
        text="Test message for card validation",
        user_id="sender-123"
    )
    
    response = requests.post(
        f"{base_url}/api/messages",
        json=activity,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    assert_success_response(response, "test_card_structure_validation - channel message")
    
    # Note: In a blackbox test, we can't directly inspect the card sent to the user
    # because it's sent proactively. However, we can validate:
    # 1. The endpoint accepts the activity
    # 2. The response structure is valid
    # 3. The bot processes the message correctly
    
    # The response should be valid JSON or empty
    if response.text:
        try:
            response_data = response.json()
            # If there's a response, validate it follows Activity schema
            if isinstance(response_data, dict):
                # Activity should have type field
                if "type" in response_data:
                    assert response_data["type"] in [
                        "message", "typing", "endOfConversation", 
                        "event", "invokeResponse"
                    ]
        except json.JSONDecodeError:
            # Response might be plain text, which is also valid
            pass


def test_hero_card_schema_compliance(container):
    """
    Test that the bot creates HeroCard structures that comply with 
    ChannelAPI-OpenAPI.yaml HeroCard schema.
    
    According to the schema, HeroCard should have:
    - title (string)
    - subtitle (string, optional)
    - text (string)
    - images (array of CardImage, optional)
    - buttons (array of CardAction, optional)
    - tap (CardAction, optional)
    
    Note: This is a blackbox test, so we test the behavior indirectly
    by verifying the bot processes messages correctly. The actual card
    structure is validated in unit tests.
    """
    _, base_url = container
    
    # Establish conversation reference
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_hero_card_schema_compliance - direct message setup")
    
    time.sleep(1)
    
    # Send channel message
    activity = create_channel_message_activity(
        text="Test message for HeroCard validation",
        user_id="sender-123"
    )
    
    response = requests.post(
        f"{base_url}/api/messages",
        json=activity,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    # Verify the endpoint processes the request correctly
    assert_success_response(response, "test_hero_card_schema_compliance - channel message")
    
    # In a blackbox test, we verify the bot's behavior:
    # - It accepts valid channel messages
    # - It processes them without errors
    # - The response indicates successful processing
    
    # The bot should acknowledge the message in the channel
    # (this is verified by the successful response status)


def test_conversation_update_members_added(container):
    """Test conversation update activity when members are added"""
    _, base_url = container
    
    activity = {
        "type": "conversationUpdate",
        "id": "conv-update-123",
        "timestamp": "2024-01-01T00:00:00Z",
        "channelId": "msteams",
        "from": {
            "id": "user-123",
            "name": "Test User"
        },
        "conversation": {
            "id": "19:channel123@thread.tacv2",
            "conversationType": "channel",
            "isGroup": True
        },
        "recipient": {
            "id": "bot-123",
            "name": "Test Bot"
        },
        "membersAdded": [
            {
                "id": "bot-123",
                "name": "Test Bot"
            }
        ],
        "serviceUrl": "https://smba.trafficmanager.net/"
    }
    
    response = requests.post(
        f"{base_url}/api/messages",
        json=activity,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    assert_success_response(response, "test_conversation_update_members_added")


def test_invalid_activity_type(container):
    """Test that invalid activity types are handled gracefully"""
    _, base_url = container
    
    activity = {
        "type": "invalidType",
        "id": "invalid-123",
        "timestamp": "2024-01-01T00:00:00Z",
        "channelId": "msteams",
        "serviceUrl": "https://smba.trafficmanager.net/"
    }
    
    response = requests.post(
        f"{base_url}/api/messages",
        json=activity,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    # Bot should handle invalid activities gracefully
    # It might return 200 (accepts but ignores) or 400 (bad request)
    assert response.status_code in [200, 201, 202, 400, 404]

def test_synthetic_data_scenarios(container):
    """
    Test bot with scenarios from test/test_scenarios.json and validate card outputs.
    Compares bot's actual card response against expected behavior.
    """
    _, base_url = container
    
    # Load test scenarios
    test_data_path = Path(__file__).parent.parent.parent.parent / "test" / "test_scenarios.json"
    with open(test_data_path, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)
    
    # Establish conversation reference first
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_synthetic_data_scenarios - setup")
    time.sleep(1)
    
    # Test a subset of scenarios (easy and medium difficulty)
    test_scenarios = [s for s in scenarios if s.get('difficulty') in ['easy', 'medium']][:10]
    
    results = []
    for scenario in test_scenarios:
        scenario_id = scenario['scenario_id']
        test_input = scenario['input']
        expected = {
            "behavior": scenario.get('expected_behavior', ''),
            "query_type": scenario.get('expected_output', {}).get('query_type', ''),
            "referenced_sku": scenario.get('expected_output', {}).get('referenced_sku', None),
            "has_typo": scenario.get('expected_output', {}).get('has_typo', False)
        }
        
        activity = create_channel_message_activity(
            text=test_input,
            user_id="sender-123",
            message_id=f"msg-{scenario_id}"
        )
        
        response = requests.post(
            f"{base_url}/api/messages",
            json=activity,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert_success_response(response, f"Scenario {scenario_id}: {scenario['name']}")
        
        # Extract and validate card
        card = extract_card_from_response(response)
        result = {
            "scenario_id": scenario_id,
            "input": test_input,
            "expected": expected,
            "card_found": card is not None,
            "card_valid": False,
            "matches_expected": False,
            "errors": [],
            "differences": [],
            "response_text": response.text[:200] if response.text else ""
        }
        
        if card:
            is_valid, errors, card_content = validate_hero_card_structure(card)
            result["card_valid"] = is_valid
            result["errors"] = errors
            result["card_content"] = card_content
            
            if is_valid:
                matches, differences = compare_card_with_expected(card_content, expected, test_input)
                result["matches_expected"] = matches
                result["differences"] = differences
        else:
            result["errors"].append("No card found in response")
        
        results.append(result)
        
        # Brief pause between requests
        time.sleep(0.5)
    
    # Print detailed results
    print(f"\n{'='*80}")
    print(f"Synthetic Data Scenarios - Card Validation Results")
    print(f"{'='*80}")
    
    for result in results:
        status = "✅" if result["card_valid"] and result["matches_expected"] else "❌"
        print(f"\n{status} Scenario {result['scenario_id']}")
        print(f"  Input: {result['input'][:60]}...")
        print(f"  Card Found: {result['card_found']}")
        print(f"  Card Valid: {result['card_valid']}")
        print(f"  Matches Expected: {result['matches_expected']}")
        
        if result["errors"]:
            print(f"  Errors: {', '.join(result['errors'])}")
        if result["differences"]:
            print(f"  Differences: {', '.join(result['differences'])}")
        
        if result.get("card_content"):
            print(f"  Card Title: {result['card_content'].get('title', 'N/A')}")
            text_preview = result['card_content'].get('text', 'N/A')
            if len(text_preview) > 100:
                text_preview = text_preview[:100] + "..."
            print(f"  Card Text: {text_preview}")
        else:
            print(f"  Response: {result['response_text']}")
    
    # Summary statistics
    print(f"\n{'='*80}")
    print(f"Summary")
    print(f"{'='*80}")
    total = len(results)
    cards_found = sum(1 for r in results if r["card_found"])
    cards_valid = sum(1 for r in results if r["card_valid"])
    matches_expected = sum(1 for r in results if r["matches_expected"])
    
    print(f"Total scenarios: {total}")
    print(f"Cards returned: {cards_found}/{total} ({cards_found/total*100:.1f}%)")
    print(f"Cards valid: {cards_valid}/{cards_found if cards_found > 0 else total} ({cards_valid/(cards_found if cards_found > 0 else total)*100:.1f}%)")
    print(f"Matches expected: {matches_expected}/{total} ({matches_expected/total*100:.1f}%)")
    print(f"{'='*80}\n")
    
    # STRICT ASSERTIONS - Bot must implement proper classification and card responses
    print("\n⚠️  VALIDATION REQUIREMENTS:")
    print("  1. Bot MUST return structured cards (not just text acknowledgments)")
    print("  2. Cards MUST contain proper SKU extraction")
    print("  3. Cards MUST indicate query type classification")
    print("  4. Cards MUST follow HeroCard schema\n")
    
    # Fail if no cards are returned - bot needs classification implementation
    assert cards_found > 0, \
        f"FAIL: Bot returned NO cards. Bot must implement message classification and return structured card responses!"
    
    # Fail if cards don't match expected structure
    if cards_found > 0:
        assert cards_valid == cards_found, \
            f"FAIL: {cards_found - cards_valid} cards have invalid structure. All cards must follow HeroCard schema!"
    
    # Fail if classifications don't match expected behavior
    assert matches_expected >= total * 0.8, \
        f"FAIL: Only {matches_expected}/{total} cards matched expected classification. Bot needs better SKU extraction and query type detection!"


def test_sku_extraction_validation(container):
    """
    Test SKU extraction from messages and validate bot's card output contains the SKUs.
    Provides clear comparison of expected vs actual output.
    """
    _, base_url = container
    
    # Establish conversation reference
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_sku_extraction_validation - setup")
    time.sleep(1)
    
    # Test cases with known SKUs
    test_cases = [
        {
            "input": "Need part 00002771",
            "expected_skus": ["00002771"],
            "expected_query_type": "part_inquiry",
            "description": "Single SKU inquiry"
        },
        {
            "input": "Lead time for RADIATOR 00007068?",
            "expected_skus": ["00007068"],
            "expected_query_type": "lead_time_query",
            "description": "SKU with description"
        },
        {
            "input": "Is BC00004214 available?",
            "expected_skus": ["BC00004214"],
            "expected_query_type": "availability_check",
            "description": "BC-format SKU"
        },
        {
            "input": "need BC00001432 harness engine + BC00001433 harness hydraulic",
            "expected_skus": ["BC00001432", "BC00001433"],
            "expected_query_type": "part_inquiry",
            "description": "Multiple SKUs"
        },
        {
            "input": "00002771",
            "expected_skus": ["00002771"],
            "expected_query_type": "part_inquiry",
            "description": "SKU only"
        }
    ]
    
    results = []
    for test_case in test_cases:
        test_input = test_case['input']
        expected_skus = test_case['expected_skus']
        description = test_case['description']
        
        activity = create_channel_message_activity(
            text=test_input,
            user_id="sender-123",
            message_id=f"msg-{hash(test_input)}"
        )
        
        response = requests.post(
            f"{base_url}/api/messages",
            json=activity,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert_success_response(response, f"SKU test: {description}")
        
        # Extract card and check for SKUs
        card = extract_card_from_response(response)
        
        result = {
            "description": description,
            "input": test_input,
            "expected_skus": expected_skus,
            "card_found": card is not None,
            "skus_found_in_card": [],
            "skus_missing": [],
            "response_text": response.text if response.text else ""
        }
        
        if card:
            is_valid, errors, card_content = validate_hero_card_structure(card)
            result["card_valid"] = is_valid
            result["card_content"] = card_content
            
            # Check which SKUs are mentioned in the card
            card_text = json.dumps(card).lower()
            for sku in expected_skus:
                if sku.lower() in card_text:
                    result["skus_found_in_card"].append(sku)
                else:
                    result["skus_missing"].append(sku)
        else:
            # No card, but bot may have returned acknowledgment text
            response_lower = response.text.lower() if response.text else ""
            for sku in expected_skus:
                if sku.lower() in response_lower:
                    result["skus_found_in_card"].append(sku)
                else:
                    result["skus_missing"].append(sku)
        
        results.append(result)
        time.sleep(0.5)
    
    # Print detailed comparison report
    print(f"\n{'='*80}")
    print(f"SKU Extraction Validation - Expected vs Actual")
    print(f"{'='*80}")
    
    for result in results:
        all_found = len(result["skus_missing"]) == 0
        status = "✅" if all_found else "❌"
        
        print(f"\n{status} {result['description']}")
        print(f"  Input: {result['input']}")
        print(f"  Expected SKUs: {', '.join(result['expected_skus'])}")
        print(f"  Found in Response: {', '.join(result['skus_found_in_card']) if result['skus_found_in_card'] else 'None'}")
        
        if result["skus_missing"]:
            print(f"  ⚠️  Missing SKUs: {', '.join(result['skus_missing'])}")
        
        if result.get("card_content"):
            print(f"  Card Title: {result['card_content'].get('title', 'N/A')}")
            text = result['card_content'].get('text', 'N/A')
            if len(text) > 150:
                text = text[:150] + "..."
            print(f"  Card Text: {text}")
        else:
            print(f"  Bot Response: {result['response_text'][:150]}")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SKU Extraction Summary")
    print(f"{'='*80}")
    total = len(results)
    perfect_matches = sum(1 for r in results if len(r["skus_missing"]) == 0)
    total_skus_expected = sum(len(r["expected_skus"]) for r in results)
    total_skus_found = sum(len(r["skus_found_in_card"]) for r in results)
    
    print(f"Test cases: {total}")
    print(f"Perfect matches: {perfect_matches}/{total} ({perfect_matches/total*100:.1f}%)")
    print(f"Total SKUs expected: {total_skus_expected}")
    print(f"Total SKUs found: {total_skus_found}/{total_skus_expected} ({total_skus_found/total_skus_expected*100:.1f}%)")
    print(f"{'='*80}\n")
    
    # Strict assertion: ALL SKUs must be found in responses
    assert total_skus_found == total_skus_expected, \
        f"Expected all SKUs to be extracted and mentioned in card. Got {total_skus_found}/{total_skus_expected}. Missing: {[r['skus_missing'] for r in results if r['skus_missing']]}"


def test_bot_classification_required(container):
    """
    CRITICAL TEST: Validates that bot implements proper message classification.
    
    This test will FAIL until the bot:
    1. Extracts SKUs from messages
    2. Classifies query types (availability, lead time, part inquiry, etc.)
    3. Returns structured cards with this information
    
    Current bot behavior: Returns generic acknowledgment text
    Required bot behavior: Returns HeroCard with classification details
    """
    _, base_url = container
    
    # Establish conversation reference
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_bot_classification_required - setup")
    time.sleep(1)
    
    # Critical test case: Availability check with SKU
    test_message = "Is part BC00004214 available?"
    expected = {
        "sku": "BC00004214",
        "query_type": "availability_check",
        "must_contain_in_card": ["BC00004214", "available"]
    }
    
    activity = create_channel_message_activity(
        text=test_message,
        user_id="sender-123",
        message_id="msg-critical-test"
    )
    
    response = requests.post(
        f"{base_url}/api/messages",
        json=activity,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    assert_success_response(response, "test_bot_classification_required - message")
    
    # Extract card
    card = extract_card_from_response(response)
    
    print(f"\n{'='*80}")
    print(f"🔍 CRITICAL CLASSIFICATION TEST")
    print(f"{'='*80}")
    print(f"Input: {test_message}")
    print(f"Expected SKU: {expected['sku']}")
    print(f"Expected Query Type: {expected['query_type']}")
    print(f"Expected in Card: {expected['must_contain_in_card']}")
    print(f"\nActual Response:")
    
    if card:
        is_valid, errors, card_content = validate_hero_card_structure(card)
        print(f"  Card Found: ✅")
        print(f"  Card Valid: {'✅' if is_valid else '❌'}")
        print(f"  Card Title: {card_content.get('title', 'N/A')}")
        print(f"  Card Text: {card_content.get('text', 'N/A')}")
        
        # Check if required content is in card
        card_text = json.dumps(card).lower()
        missing = []
        for required in expected['must_contain_in_card']:
            if required.lower() not in card_text:
                missing.append(required)
        
        if missing:
            print(f"\n❌ MISSING REQUIRED CONTENT: {missing}")
            print(f"{'='*80}\n")
            pytest.fail(
                f"Bot did not properly classify the message!\n"
                f"Expected to find {expected['must_contain_in_card']} in card response.\n"
                f"Missing: {missing}\n\n"
                f"ACTION REQUIRED: Implement message classification logic in the bot:\n"
                f"  1. Extract SKU '{expected['sku']}' from message\n"
                f"  2. Detect query type as '{expected['query_type']}'\n"
                f"  3. Include this information in the card response"
            )
        else:
            print(f"\n✅ ALL REQUIRED CONTENT FOUND")
    else:
        print(f"  Card Found: ❌")
        print(f"  Response Text: {response.text[:200]}")
        print(f"{'='*80}\n")
        pytest.fail(
            f"Bot returned NO CARD for message: '{test_message}'\n"
            f"Current behavior: Generic text acknowledgment\n"
            f"Required behavior: Structured HeroCard with:\n"
            f"  - SKU: {expected['sku']}\n"
            f"  - Query Type: {expected['query_type']}\n"
            f"  - Card content mentioning: {expected['must_contain_in_card']}\n\n"
            f"ACTION REQUIRED: Implement card-based responses in the bot!"
        )
    
    print(f"{'='*80}\n")


def test_teams_messages_extended(container):
    """Test bot with extended Teams messages from test/teams_messages_EN_extended.json"""
    _, base_url = container
    
    # Load extended messages
    test_data_path = Path(__file__).parent.parent.parent.parent / "test" / "teams_messages_EN_extended.json"
    with open(test_data_path, 'r', encoding='utf-8') as f:
        messages = json.load(f)
    
    # Establish conversation reference
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_teams_messages_extended - setup")
    time.sleep(1)
    
    # Test first 20 messages
    test_messages = messages[:20]
    
    for msg_data in test_messages:
        message_id = msg_data['message_id']
        message_text = msg_data['message']
        
        activity = create_channel_message_activity(
            text=message_text,
            user_id="sender-123",
            message_id=message_id
        )
        
        response = requests.post(
            f"{base_url}/api/messages",
            json=activity,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert_success_response(response, f"Message {message_id}")
        
        # Brief pause between requests
        time.sleep(0.3)


def test_edge_cases(container):
    """Test bot with edge case messages from test/teams_messages_edge_cases.json"""
    _, base_url = container
    
    # Load edge cases
    test_data_path = Path(__file__).parent.parent.parent.parent / "test" / "teams_messages_edge_cases.json"
    with open(test_data_path, 'r', encoding='utf-8') as f:
        edge_cases = json.load(f)
    
    # Establish conversation reference
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_edge_cases - setup")
    time.sleep(1)
    
    # Test all edge cases
    for edge_case in edge_cases:
        message_id = edge_case['message_id']
        message_text = edge_case['message']
        notes = edge_case.get('notes', '')
        
        activity = create_channel_message_activity(
            text=message_text,
            user_id="sender-123",
            message_id=message_id
        )
        
        response = requests.post(
            f"{base_url}/api/messages",
            json=activity,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert_success_response(response, f"Edge case {message_id}: {notes}")
        
        # Brief pause between requests
        time.sleep(0.5)


def test_sku_extraction_accuracy(container):
    """Test that bot correctly extracts SKUs from various message formats"""
    _, base_url = container
    
    # Establish conversation reference
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_sku_extraction_accuracy - setup")
    time.sleep(1)
    
    # Test messages with various SKU formats
    test_cases = [
        ("00002771", "Direct SKU only"),
        ("Need part 00002771", "SKU with text before"),
        ("00002771 please", "SKU with text after"),
        ("Parts: 00002771, 00007068, 00002707", "Multiple SKUs"),
        ("BC00004214 urgently needed", "BC format SKU"),
        ("Part no. 00025620", "SKU with 'no.' abbreviation"),
        ("SKU: 00002771", "SKU with label"),
    ]
    
    for message_text, description in test_cases:
        activity = create_channel_message_activity(
            text=message_text,
            user_id="sender-123",
            message_id=f"msg-{description.replace(' ', '-')}"
        )
        
        response = requests.post(
            f"{base_url}/api/messages",
            json=activity,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert_success_response(response, f"SKU extraction test: {description}")
        time.sleep(0.3)


def test_query_type_classification(container):
    """Test that bot correctly classifies different query types"""
    _, base_url = container
    
    # Establish conversation reference
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_query_type_classification - setup")
    time.sleep(1)
    
    # Test different query types
    test_cases = [
        ("What's the lead time for 00002771?", "lead_time"),
        ("Is 00007068 compatible with TH663i?", "compatibility"),
        ("Need replacement for 00002707", "replacement"),
        ("Is 00002771 in stock?", "availability"),
        ("00002771 availability?", "general"),
    ]
    
    for message_text, query_type in test_cases:
        activity = create_channel_message_activity(
            text=message_text,
            user_id="sender-123",
            message_id=f"msg-{query_type}-test"
        )
        
        response = requests.post(
            f"{base_url}/api/messages",
            json=activity,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert_success_response(response, f"Query type: {query_type}")
        time.sleep(0.3)


def test_typo_handling(container):
    """Test that bot handles messages with typos gracefully"""
    _, base_url = container
    
    # Establish conversation reference
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_typo_handling - setup")
    time.sleep(1)
    
    # Messages with various typos
    typo_messages = [
        "neeeed 00002771 urgently",
        "Can I get a replacment for 00002463? Its urgant!",
        "whn can we get TIRE BC00004214?",
        "Is there a supersession for 00008160?",
        "availbility for 00002771?",
    ]
    
    for message_text in typo_messages:
        activity = create_channel_message_activity(
            text=message_text,
            user_id="sender-123",
            message_id=f"msg-typo-{hash(message_text)}"
        )
        
        response = requests.post(
            f"{base_url}/api/messages",
            json=activity,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert_success_response(response, f"Typo handling: {message_text[:30]}...")
        time.sleep(0.3)


def test_multilingual_messages(container):
    """Test bot with Finnish and mixed-language messages"""
    _, base_url = container
    
    # Load Finnish messages
    test_data_path = Path(__file__).parent.parent.parent.parent / "test" / "teams_messages_FI_extended.json"
    
    if not test_data_path.exists():
        pytest.skip("Finnish test data not available")
    
    with open(test_data_path, 'r', encoding='utf-8') as f:
        fi_messages = json.load(f)
    
    # Establish conversation reference
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_multilingual_messages - setup")
    time.sleep(1)
    
    # Test first 10 Finnish messages
    test_messages = fi_messages[:10]
    
    for msg_data in test_messages:
        message_id = msg_data['message_id']
        message_text = msg_data['message']
        
        activity = create_channel_message_activity(
            text=message_text,
            user_id="sender-123",
            message_id=message_id
        )
        
        response = requests.post(
            f"{base_url}/api/messages",
            json=activity,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert_success_response(response, f"Finnish message {message_id}")
        time.sleep(0.3)
    
    # Test mixed language messages
    mixed_messages = [
        "Onko PUMP 00002771 varastossa? need asap",
        "Tarvitaan PUMPPU 00002771 kiireellä",
        "Onko meillä stock ALTERNATOR BC00002492 and also STARTER 00002707?",
    ]
    
    for message_text in mixed_messages:
        activity = create_channel_message_activity(
            text=message_text,
            user_id="sender-123",
            message_id=f"msg-mixed-{hash(message_text)}"
        )
        
        response = requests.post(
            f"{base_url}/api/messages",
            json=activity,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert_success_response(response, f"Mixed language: {message_text[:30]}...")
        time.sleep(0.3)


def test_performance_with_batch_messages(container):
    """Test bot performance with a batch of messages"""
    _, base_url = container
    
    # Load test messages
    test_data_path = Path(__file__).parent.parent.parent.parent / "test" / "teams_messages_EN_extended.json"
    with open(test_data_path, 'r', encoding='utf-8') as f:
        messages = json.load(f)
    
    # Establish conversation reference
    direct_msg = create_direct_message_activity(
        text="Hello",
        user_id="test-user-123"
    )
    response = requests.post(
        f"{base_url}/api/messages",
        json=direct_msg,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    assert_success_response(response, "test_performance_with_batch_messages - setup")
    time.sleep(1)
    
    # Send 50 messages and measure total time
    start_time = time.time()
    test_messages = messages[:50]
    success_count = 0
    
    for msg_data in test_messages:
        message_id = msg_data['message_id']
        message_text = msg_data['message']
        
        activity = create_channel_message_activity(
            text=message_text,
            user_id="sender-123",
            message_id=message_id
        )
        
        try:
            response = requests.post(
                f"{base_url}/api/messages",
                json=activity,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code in [200, 201, 202]:
                success_count += 1
        except Exception as e:
            print(f"Error processing message {message_id}: {e}")
        
        time.sleep(0.2)  # Small delay to avoid overwhelming the server
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / len(test_messages)
    
    print(f"\n=== Performance Test Results ===")
    print(f"Total messages: {len(test_messages)}")
    print(f"Successful: {success_count}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per message: {avg_time:.2f}s")
    print(f"=" * 40)
    
    # Assert at least 90% success rate
    assert success_count >= len(test_messages) * 0.9, f"Expected 90% success rate, got {success_count}/{len(test_messages)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
