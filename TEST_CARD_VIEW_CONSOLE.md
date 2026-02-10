# Test Card View in Browser Console

## Quick Test (Multiple Cards)

Run this in the browser console on `/api/dev/card-preview`:

```javascript
(async () => {
  // Use longer text to get multiple segments (needs >100 chars for 3+ segments)
  const testText = `
Understanding Machine Learning Fundamentals

Machine learning enables computers to learn from data without explicit programming. This powerful technology has transformed many industries.

Key Concepts:
- Supervised learning uses labeled examples to train models
- Unsupervised learning finds hidden patterns in data
- Reinforcement learning learns from rewards and penalties

Neural Networks:
Neural networks consist of interconnected nodes organized in layers. The input layer receives data, hidden layers process information, and the output layer produces results.

Training Process:
1. Forward propagation passes data through network
2. Loss calculation measures prediction error
3. Backpropagation adjusts weights
4. Iteration repeats until convergence

Applications include image recognition, natural language processing, and autonomous vehicles.
  `.trim();

  const res = await fetch('/api/dev/card-segments', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
    },
    body: JSON.stringify({ text: testText })
  });

  const data = await res.json();
  console.log('API Response:', data);
  console.log('Segments count:', data.segments?.length || 0);

  // Map segments to cards format (API returns 'segments', not 'cards')
  const cards = (data.segments || []).map((seg, i) => ({
    header: seg.header || `Card ${i + 1}`,
    body: seg.body || '',
    card_key: seg.card_key || `preview-${i}`,
    segment_index: seg.segment_index ?? i
  }));

  console.log('Mapped cards:', cards);
  console.log('Cards count:', cards.length);

  // Set data and render
  if (typeof CardOverlay !== 'undefined') {
    CardOverlay.setCardsData(cards);
    CardOverlay.renderGrid(cards);
    
    // Verify rendering
    const rendered = document.querySelectorAll('.cv-grid-card').length;
    console.log('✅ Rendered cards:', rendered);
    console.log('✅ State cards:', CardOverlay.state.cards?.length);
    
    // Check first card
    console.log('First card:', CardOverlay.state.cards?.[0]);
  } else {
    console.error('❌ CardOverlay not loaded!');
  }
})();
```

## Expected Output

- **Segments count**: 3-9 (depending on text length)
- **Rendered cards**: Should match segments count
- **State cards**: Should match segments count

## Debugging

If you only get 1 card:
- Text is too short (<100 chars) → Use longer test text
- Check `data.segments` array length
- Verify `CardOverlay.renderGrid()` is being called

If cards don't render:
- Check browser console for errors
- Verify `#cards-container` element exists
- Check CSS is loaded (`card-overlay.css`)

## Verify Container Exists

```javascript
// Check if container exists
const container = document.getElementById('cards-container');
console.log('Container:', container);
console.log('Container HTML:', container?.innerHTML);
```


