// DOM Elements
const connectWalletBtn = document.getElementById('connectWalletBtn');
const walletConnect = document.getElementById('walletConnect');
const walletOptions = document.querySelectorAll('.wallet-option');

// Toggle wallet connection modal
connectWalletBtn.addEventListener('click', () => {
    if (walletConnect.style.display === 'none' || walletConnect.style.display === '') {
        walletConnect.style.display = 'block';
    } else {
        walletConnect.style.display = 'none';
    }
});

// Close wallet modal when clicking outside
document.addEventListener('click', (event) => {
    if (!walletConnect.contains(event.target) && event.target !== connectWalletBtn) {
        walletConnect.style.display = 'none';
    }
});

// Wallet connection functionality
walletOptions.forEach(option => {
    option.addEventListener('click', async () => {
        const walletName = option.querySelector('p').textContent;
        
        try {
            // Display connecting state
            connectWalletBtn.textContent = `Connecting to ${walletName}...`;
            
            // This is where you would connect to the actual wallet
            // For demonstration purposes, we'll use a timeout to simulate connection
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            // Simulate successful connection
            connectWalletBtn.textContent = 'Wallet Connected';
            connectWalletBtn.classList.add('connected');
            walletConnect.style.display = 'none';
            
            // Mock address display
            const mockAddress = '0x' + Math.random().toString(16).substr(2, 10) + '...';
            connectWalletBtn.textContent = mockAddress;
            
            // You would typically store the wallet connection in state or local storage
            localStorage.setItem('walletConnected', 'true');
            localStorage.setItem('walletType', walletName);
            
        } catch (error) {
            console.error('Error connecting wallet:', error);
            connectWalletBtn.textContent = 'Connection Failed';
            
            // Reset after a delay
            setTimeout(() => {
                connectWalletBtn.textContent = 'Connect Wallet';
            }, 2000);
        }
    });
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            window.scrollTo({
                top: target.offsetTop - 100,
                behavior: 'smooth'
            });
        }
    });
});

// Check if user has previously connected wallet
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('walletConnected') === 'true') {
        connectWalletBtn.textContent = '0x' + Math.random().toString(16).substr(2, 10) + '...';
        connectWalletBtn.classList.add('connected');
    }
    
    // Add animation to feature cards on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, { threshold: 0.2 });
    
    document.querySelectorAll('.feature-card').forEach(card => {
        observer.observe(card);
    });
});

// Form validation for newsletter subscription (add this in your HTML as needed)
const subscribeForm = document.getElementById('subscribe-form');
if (subscribeForm) {
    subscribeForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('email-input').value;
        
        if (!email || !email.includes('@')) {
            alert('Please enter a valid email address');
            return;
        }
        
        // Simulate API call
        setTimeout(() => {
            alert('Thank you for subscribing to our newsletter!');
            subscribeForm.reset();
        }, 1000);
    });
}

// Web3 connection helpers (these would be expanded in a real application)
async function detectWallet() {
    if (window.ethereum) {
        return 'MetaMask';
    } else if (window.solana) {
        return 'Phantom';
    } else {
        return null;
    }
}

async function connectToMetaMask() {
    if (window.ethereum) {
        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            return accounts[0];
        } catch (error) {
            console.error('User denied account access');
            throw error;
        }
    } else {
        throw new Error('MetaMask not installed');
    }
}

// Mobile menu toggle functionality
const menuToggle = document.querySelector('.menu-toggle');
const navMenu = document.querySelector('nav ul');

if (menuToggle) {
    menuToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });
}