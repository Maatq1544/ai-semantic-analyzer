## Summary

<!-- 1-3 sentences. What does this PR change and why. -->

## Related Issue

<!-- Fixes #123 / Closes #123 / Relates to #123 -->

## Type of Change

<!-- Check the relevant boxes, delete the rest -->

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that breaks existing behavior)
- [ ] 📝 Documentation update
- [ ] ♻️ Refactor (no functional change)
- [ ] ⚡ Performance improvement
- [ ] ✅ Test update
- [ ] 🔧 Build / CI change

## Changes

<!-- Concrete list of changes. Group by file or area. -->

- Added `Foo.bar()` to `baz.py`
- Updated `config.py` to support new env var
- Added tests in `tests/test_baz.py`

## Testing

<!-- What you tested, how to reproduce -->

- [ ] Unit tests pass (`pytest`)
- [ ] Linter passes (`ruff check`)
- [ ] Type checker passes (`mypy src/`)
- [ ] Manual smoke test done

**How to test:**

1. Set `DEEPSEEK_API_KEY=...`
2. Run `semantic-analyzer run examples/sample_reviews.csv "Extract sentiment"`
3. Expected: `analyzed_sample_reviews.csv` with `sentiment` column

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented hard-to-understand areas
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally
- [ ] Any dependent changes are merged

## Additional Notes

<!-- Breaking changes, follow-up work, screenshots, anything reviewers should know -->
