# Step 14: Retry Mechanisms

## What Was Done

Implemented comprehensive retry mechanisms for unclear concepts and low scores:

1. **RetryManager Class** (`agent/core/retry_manager.py`):
   - Manages retry logic with `MAX_RETRIES = 3` constant
   - Tracks retry counts and determines retry eligibility
   - Provides retry strategies based on attempt number
   - Generates context for re-teaching

2. **Retry Methods**:
   - `should_retry()`: Determines if concept should be retried based on quiz score (< 0.6 threshold)
   - `can_retry()`: Checks if retries are still available (< MAX_RETRIES)
   - `mark_for_retry()`: Marks concept for retry and increments retry count
   - `get_retry_strategy()`: Determines retry strategy (simplify_explanation, alternative_approach, adapt_difficulty)
   - `get_reteaching_context()`: Generates context string for re-teaching with retry history
   - `should_adapt_difficulty()`: Checks if difficulty should be adapted instead of retrying
   - `get_concepts_exceeding_retries()`: Returns list of concepts that exceeded max retries
   - `reset_retry_for_concept()`: Resets retry count (e.g., after successful adaptation)

3. **Retry Strategies**:
   - **Retry 1**: `simplify_explanation` - Use simpler language, more examples, analogies
   - **Retry 2**: `alternative_approach` - Try different teaching method, visual examples, step-by-step breakdown
   - **Retry 3**: `adapt_difficulty` - Decrease difficulty level before final retry
   - **After Max Retries**: Adapt difficulty instead of retrying

4. **Enhanced Teacher Tool** (`agent/tools/teacher_tool.py`):
   - Added `retry_attempt` parameter to support retry-specific instructions
   - Added `alternative_strategy` parameter for explicit strategy selection
   - Enhanced prompt with retry-specific instructions:
     - Retry 1: Simpler language, more examples, analogies
     - Retry 2: Completely different approach, visual examples
     - Retry 3+: Simplest explanation, core essentials only

5. **Integration with DecisionRules**:
   - Uses RetryManager to determine retry strategies
   - Passes retry context and strategy to teaching tool
   - Handles concepts exceeding max retries by adapting difficulty

6. **Integration with ToolExecutor**:
   - Uses RetryManager when evaluating quiz responses
   - Automatically marks concepts for retry on low scores (< 0.6)
   - Prevents double-incrementing retry counts

7. **Retry Limits**:
   - `MAX_RETRIES = 3`: Maximum number of retry attempts
   - `LOW_SCORE_THRESHOLD = 0.6`: Score threshold for triggering retry
   - Prevents infinite loops by enforcing limits

8. **Alternative Explanations**:
   - Strategy-based explanations that vary by retry attempt
   - Context-aware re-teaching with performance history
   - Different teaching approaches for each retry attempt

## Why This Is Required

Retry mechanisms are essential because:

1. **Error Recovery**: Enables the system to recover from learning failures and adapt to learner needs.

2. **Retry Counting**: Tracks retry attempts to prevent infinite loops and enforce limits.

3. **Re-explanation Logic**: Provides structured re-explanation with alternative strategies for each retry attempt.

4. **Low Score Handling**: Automatically triggers retry when quiz scores are below threshold (< 0.6).

5. **Retry Limits**: Enforces maximum retry attempts (3) to prevent infinite retry loops.

6. **Alternative Strategies**: Uses different teaching approaches for each retry:
   - First retry: Simplify
   - Second retry: Alternative approach
   - Third retry: Decrease difficulty
   - After max: Adapt difficulty

7. **Loop Prevention**: Prevents infinite loops by:
   - Enforcing MAX_RETRIES limit
   - Adapting difficulty after max retries
   - Tracking concepts exceeding retries

8. **Performance-Based Adaptation**: Adapts teaching strategy based on learner performance history.

9. **State Consistency**: Properly tracks retry counts and status in state without double-incrementing.

10. **Foundation for Adaptive Learning**: Provides the core mechanism for handling learning difficulties and adapting to learner needs.

Without retry mechanisms, the system would fail to handle learning difficulties, leading to poor learning outcomes and inability to adapt to individual learner needs.

