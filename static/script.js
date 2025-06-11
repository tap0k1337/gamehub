let currentSlide = 0

function startCarousel() {
	const slides = document.querySelectorAll('.carousel-item')
	if (!slides.length) return

	function showSlide(index) {
		slides.forEach((slide, i) => {
			slide.style.display = i === index ? 'block' : 'none'
		})
	}

	showSlide(currentSlide)
	setInterval(() => {
		currentSlide = (currentSlide + 1) % slides.length
		showSlide(currentSlide)
	}, 3000)
}

// Добавляем товар в корзину (требуется вызвать addToCart(id, name, price))
function addToCart(id, name, price) {
	let cart = JSON.parse(localStorage.getItem('cart')) || []
	const item = cart.find(product => product.id === id)
	if (item) {
		item.quantity++
	} else {
		cart.push({ id, name, price, quantity: 1 })
	}
	localStorage.setItem('cart', JSON.stringify(cart))
	updateCartDisplay()
	showNotification(`"${name}" добавлен в корзину`)
}

// Удаляем товар из корзины по id
function removeFromCart(id) {
	let cart = JSON.parse(localStorage.getItem('cart')) || []
	cart = cart.filter(product => product.id !== id)
	localStorage.setItem('cart', JSON.stringify(cart))
	updateCartDisplay()
	showNotification(`Товар удалён из корзины`)
}

// Обновляем отображение корзины
function updateCartDisplay() {
	const cart = JSON.parse(localStorage.getItem('cart')) || []
	const list = document.getElementById('cart-items')
	const totalEl = document.getElementById('cart-total')
	if (!list || !totalEl) return

	list.innerHTML = ''
	let total = 0
	cart.forEach(product => {
		const li = document.createElement('li')
		li.textContent = `${product.name} – ${product.price} руб. x ${product.quantity}`

		const removeBtn = document.createElement('button')
		removeBtn.textContent = 'Удалить'
		removeBtn.onclick = () => removeFromCart(product.id)

		li.appendChild(removeBtn)
		list.appendChild(li)
		total += product.price * product.quantity
	})
	totalEl.textContent = total
}

// Показ уведомления
function showNotification(message) {
	const note = document.getElementById('notify')
	if (!note) return
	note.textContent = message
	note.style.display = 'block'
	setTimeout(() => {
		note.style.display = 'none'
	}, 3000)
}

document.addEventListener('DOMContentLoaded', () => {
	updateCartDisplay()
	startCarousel()

	const checkoutForm = document.querySelector('form')
	if (checkoutForm) {
		checkoutForm.addEventListener('submit', () => {
			// При сабмите отправляем именно JSON с id
			document.getElementById('cart-data').value =
				localStorage.getItem('cart') || '[]'
		})
	}
})
