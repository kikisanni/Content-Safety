import json

def analyze_errors():
    """
    Analyze evaluation results and display error patterns.
    Finds false positives and false negatives for each category.
    """
    
    # Load evaluation results
    with open('evaluation_results.json', 'r') as f:
        data = json.load(f)
    
    results = data['detailed_results']
    categories = ['hate_speech', 'spam', 'misinformation', 'harassment']
    
    print("="*80)
    print("ERROR ANALYSIS - Content Safety Classifier")
    print("="*80)
    
    for category in categories:
        print(f"\n{'='*80}")
        print(f"{category.upper().replace('_', ' ')}")
        print(f"{'='*80}")
        
        false_positives = []
        false_negatives = []
        
        # Find errors
        for result in results:
            gt = result['ground_truth'][category]
            pred = 1 if result['prediction'][category] else 0
            
            if gt == 0 and pred == 1:  # False positive
                false_positives.append(result)
            elif gt == 1 and pred == 0:  # False negative
                false_negatives.append(result)
        
        # Display false positives
        print(f"\nFALSE POSITIVES: {len(false_positives)}")
        print("(Model incorrectly flagged safe content)")
        print("-"*80)
        
        if false_positives:
            for i, fp in enumerate(false_positives[:5], 1):  # Show first 5
                print(f"\n{i}. Text: \"{fp['text']}\"")
                print(f"   Confidence: {fp['confidence'][category]:.2f}")
                print(f"   Model's reason: {fp['reasons'][category]}")
        else:
            print("None!")
        
        # Display false negatives
        print(f"\n\nFALSE NEGATIVES: {len(false_negatives)}")
        print("(Model missed actual violations)")
        print("-"*80)
        
        if false_negatives:
            for i, fn in enumerate(false_negatives[:5], 1):  # Show first 5
                print(f"\n{i}. Text: \"{fn['text']}\"")
                print(f"   Confidence: {fn['confidence'][category]:.2f}")
                print(f"   Model's reason: {fn['reasons'][category]}")
        else:
            print("None!")
        
        print()
    
    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    total_fp = 0
    total_fn = 0
    
    for category in categories:
        fp_count = sum(1 for r in results 
                      if r['ground_truth'][category] == 0 
                      and r['prediction'][category] == True)
        fn_count = sum(1 for r in results 
                      if r['ground_truth'][category] == 1 
                      and r['prediction'][category] == False)
        
        total_fp += fp_count
        total_fn += fn_count
        
        print(f"{category:20s} FP: {fp_count:2d}  FN: {fn_count:2d}")
    
    print("-"*80)
    print(f"{'TOTAL':20s} FP: {total_fp:2d}  FN: {total_fn:2d}")
    print(f"\nTotal samples: {len(results)}")
    print(f"Error rate: {(total_fp + total_fn) / (len(results) * 4):.1%}")


if __name__ == "__main__":
    analyze_errors()