from src.matcher import SanctionsMatcher

# Test config
config = {
    'matching': {
        'threshold': 85,
        'algorithm': 'token_sort_ratio'
    }
}

matcher = SanctionsMatcher(config)

# Test normalization
company_name = "Frank Kakorere Enterprises"
sanctions_name = "FRANK KAKORERE"

normalized_company = matcher.normalize_name(company_name)
normalized_sanctions = matcher.normalize_name(sanctions_name)

print(f"Original company: '{company_name}'")
print(f"Normalized company: '{normalized_company}'")
print(f"Original sanctions: '{sanctions_name}'")
print(f"Normalized sanctions: '{normalized_sanctions}'")
print()

# Test similarity
score = matcher.calculate_similarity(normalized_company, normalized_sanctions)
print(f"Similarity score: {score}")
print(f"Threshold: {matcher.threshold}")
print(f"Match: {score >= matcher.threshold}")