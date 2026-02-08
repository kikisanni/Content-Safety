import pandas as pd
from classifier import classify_content
import json


def load_test_data():
    '''
    Read CSV file
    Return DataFrame
    '''
    df = pd.read_csv('test_data.csv')
    # print(df)
    return df


def run_evaluation():
    '''
    For each row in test data:
        - Get text
        - Run classifier
        - Store prediction
        - Store ground truth
    Return results
    '''
    df = load_test_data()
    results = []

    for index, row in df.iterrows():
        text = row['text']
        pred = classify_content(text)

        if pred is None:
            print(f"Classifier failed for: {text[:50]}")
            continue
    
            
        # Store result with both prediction and ground truth
        result = {
            'text': text,
            'ground_truth': {
                'hate_speech': row['hate_speech'],
                'spam': row['spam'],
                'misinformation': row['misinformation'],
                'harassment': row['harassment']
            },
            'prediction': {
                'hate_speech': pred['hate_speech']['detected'],
                'spam': pred['spam']['detected'],
                'misinformation': pred['misinformation']['detected'],
                'harassment': pred['harassment']['detected']
            },
            'confidence': {
                'hate_speech': pred['hate_speech']['confidence'],
                'spam': pred['spam']['confidence'],
                'misinformation': pred['misinformation']['confidence'],
                'harassment': pred['harassment']['confidence']
            },
            'reasons': {
                'hate_speech': pred['hate_speech']['reason'],
                'spam': pred['spam']['reason'],
                'misinformation': pred['misinformation']['reason'],
                'harassment': pred['harassment']['reason']
            }
        }

        results.append(result)
    
    return results



def calculate_metrics(results, category):
    '''
    Calculate TP, TN, FP, FN
    Calculate Precision, Recall, F1

    Args:
    results: List of result dicts from run_evaluation()
    category: String like 'hate_speech', 'spam', etc.
    Return metrics dict
    '''

    # Initialise counters

    TP = 0 # True Positives
    TN = 0 # True Negatives
    FP = 0 # False Positives
    FN = 0 # False Negatives

    # Loop through results and count
    for result in results:
        ground_truth = result['ground_truth'][category]  # 0 or 1
        prediction = result['prediction'][category]       # True or False
        
        # Convert prediction to int for comparison
        pred_int = 1 if prediction else 0
        
        # Count TP, TN, FP, FN
        if ground_truth == 1 and pred_int == 1:
            TP += 1
        elif ground_truth == 0 and pred_int == 0:
            TN += 1
        elif ground_truth == 0 and pred_int == 1:
            FP += 1  # Said yes, but actually no
        elif ground_truth == 1 and pred_int == 0:
            FN += 1  # Said no, but actually yes
    
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # Calculate accuracy (bonus metric)
    total = TP + TN + FP + FN
    accuracy = (TP + TN) / total if total > 0 else 0.0
    
    return {
        'category': category,
        'TP': TP,
        'TN': TN,
        'FP': FP,
        'FN': FN,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'accuracy': accuracy,
        'total_samples': total
    }


if __name__ == "__main__":
    """
    Main execution:
    1. Run evaluation on all test data
    2. Calculate metrics for each category
    3. Print results
    4. Save results to file
    """
    
    print("="*80)
    print("EVALUATION STARTED")
    print("="*80)
    
    # Run evaluation
    print("\nRunning classifier on test dataset...")
    results = run_evaluation()
    
    print(f"\nCompleted {len(results)} evaluations")
    
    # Calculate metrics for each category
    categories = ['hate_speech', 'spam', 'misinformation', 'harassment']
    all_metrics = {}
    
    print("\n" + "="*80)
    print("METRICS BY CATEGORY")
    print("="*80)
    
    for category in categories:
        metrics = calculate_metrics(results, category)
        all_metrics[category] = metrics
        
        # Print metrics
        print(f"\n{category.upper().replace('_', ' ')}")
        print("-"*80)
        print(f"  True Positives:  {metrics['TP']:3d}  (Correctly flagged)")
        print(f"  True Negatives:  {metrics['TN']:3d}  (Correctly safe)")
        print(f"  False Positives: {metrics['FP']:3d}  (Incorrectly flagged)")
        print(f"  False Negatives: {metrics['FN']:3d}  (Missed violations)")
        print(f"  ---")
        print(f"  Precision:       {metrics['precision']:.2%}")
        print(f"  Recall:          {metrics['recall']:.2%}")
        print(f"  F1 Score:        {metrics['f1']:.2%}")
        print(f"  Accuracy:        {metrics['accuracy']:.2%}")
    
    # Save results to JSON file
    print("SAVING RESULTS.....")

    output = {
        'metrics': all_metrics,
        'detailed_results': results
    }
    
    with open('evaluation_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("Results saved to 'evaluation_results.json'")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    avg_f1 = sum(m['f1'] for m in all_metrics.values()) / len(all_metrics)
    print(f"Average F1 Score: {avg_f1:.2%}")
    print(f"Total samples evaluated: {len(results)}")