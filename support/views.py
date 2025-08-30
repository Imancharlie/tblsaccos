from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

def chatbot(request):
    # Support chatbot interface
    context = {}
    return render(request, 'support/chatbot.html', context)

@login_required
def support_tickets(request):
    # User support tickets
    context = {
        'tickets': [],  # Example: empty for now
    }
    return render(request, 'support/support_tickets.html', context)

def faq(request):
    # Frequently asked questions
    faqs = [
        {
            'question': 'How do I apply for a loan?',
            'answer': 'You can apply for a loan through the "Apply for Loan" section in your dashboard.'
        },
        {
            'question': 'How do I buy shares?',
            'answer': 'You can purchase shares through the "Buy Shares" section in your dashboard.'
        },
        {
            'question': 'What documents do I need for loan application?',
            'answer': 'You will need salary slips, bank statements, and guarantor information.'
        }
    ]
    
    context = {
        'faqs': faqs,
    }
    return render(request, 'support/faq.html', context)
