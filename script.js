const itemsList = document.getElementById('items-list');
const addItemBtn = document.getElementById('add-item-btn');
const serviceChargeInput = document.getElementById('service-charge');
const discountInput = document.getElementById('discount');
const paymentStatusSelect = document.getElementById('payment-status');
const subtotalText = document.getElementById('subtotal');
const grandTotalText = document.getElementById('grand-total');
const generatePdfBtn = document.getElementById('generate-pdf-btn');

const formatCurrency = (value) => `₹${value.toFixed(2)}`;

function createItemRow(description = '', qty = 1, rate = 0) {
  const row = document.createElement('div');
  row.className = 'item-row';

  row.innerHTML = `
    <input type="text" class="description" placeholder="Item / service description" value="${description}" />
    <input type="number" class="qty" min="0" step="1" value="${qty}" />
    <input type="number" class="rate" min="0" step="0.01" value="${rate}" />
    <button type="button" class="danger remove-item">Remove</button>
  `;

  row.querySelectorAll('input').forEach((input) => {
    input.addEventListener('input', calculateTotals);
  });

  row.querySelector('.remove-item').addEventListener('click', () => {
    row.remove();
    calculateTotals();
  });

  itemsList.appendChild(row);
}

function collectItems() {
  return [...itemsList.querySelectorAll('.item-row')]
    .map((row) => {
      const description = row.querySelector('.description').value.trim();
      const qty = parseFloat(row.querySelector('.qty').value) || 0;
      const rate = parseFloat(row.querySelector('.rate').value) || 0;
      const amount = qty * rate;
      return { description, qty, rate, amount };
    })
    .filter((item) => item.description || item.amount > 0);
}

function calculateTotals() {
  const items = collectItems();
  const subtotal = items.reduce((sum, item) => sum + item.amount, 0);
  const serviceCharge = parseFloat(serviceChargeInput.value) || 0;
  const discount = parseFloat(discountInput.value) || 0;
  const grandTotal = Math.max(0, subtotal + serviceCharge - discount);

  subtotalText.textContent = formatCurrency(subtotal);
  grandTotalText.textContent = formatCurrency(grandTotal);

  return { items, subtotal, serviceCharge, discount, grandTotal };
}

function generatePdf() {
  const { items, subtotal, serviceCharge, discount, grandTotal } = calculateTotals();
  const status = paymentStatusSelect.value;

  if (!window.jspdf || typeof window.jspdf.jsPDF !== 'function') {
    alert('PDF library is still loading. Please wait a moment and try again.');
    return;
  }

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  doc.setFontSize(18);
  doc.text('Technician Invoice', 14, 18);
  doc.setFontSize(11);
  doc.text(`Date: ${new Date().toLocaleDateString()}`, 14, 26);
  doc.text(`Payment Status: ${status}`, 14, 32);

  const rows = items.length
    ? items.map((item) => [item.description || '-', item.qty.toString(), formatCurrency(item.rate), formatCurrency(item.amount)])
    : [['No billable items', '0', formatCurrency(0), formatCurrency(0)]];

  doc.autoTable({
    startY: 38,
    head: [['Description', 'Qty', 'Rate', 'Amount']],
    body: rows,
    theme: 'striped',
    headStyles: { fillColor: [37, 99, 235] },
  });

  const finalY = doc.lastAutoTable.finalY + 10;
  doc.text(`Subtotal: ${formatCurrency(subtotal)}`, 14, finalY);
  doc.text(`Service Charge: ${formatCurrency(serviceCharge)}`, 14, finalY + 7);
  doc.text(`Discount: ${formatCurrency(discount)}`, 14, finalY + 14);
  doc.setFontSize(13);
  doc.text(`Grand Total: ${formatCurrency(grandTotal)}`, 14, finalY + 23);

  const fileDate = new Date().toISOString().split('T')[0];
  doc.save(`technician-invoice-${fileDate}.pdf`);
}

addItemBtn.addEventListener('click', () => {
  createItemRow();
});

[serviceChargeInput, discountInput, paymentStatusSelect].forEach((el) => {
  el.addEventListener('input', calculateTotals);
  el.addEventListener('change', calculateTotals);
});

generatePdfBtn.addEventListener('click', generatePdf);

createItemRow('Repair service', 1, 1500);
calculateTotals();
