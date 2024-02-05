import hashlib
from django.db import models
import uuid


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    on_chain = models.BooleanField(default=False)
    sender = models.CharField(max_length=50, default="")
    recipient = models.CharField(max_length=50, default="")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Block(models.Model):
    index = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    transactions = models.ManyToManyField(Transaction)
    prev_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64)
    nonce = models.IntegerField()

    def calculate_hash(self, transactions=None):
        transactions_count = transactions.count() if transactions else 0
        block_contents = f"{self.index}{self.timestamp}{transactions_count}{self.prev_hash}{self.nonce}"
        encoded_block = block_contents.encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def save(self, *args, **kwargs):
        # Use transactions if they have been set
        if hasattr(self, '_transactions_to_set'):
            self.hash = self.calculate_hash(transactions=self._transactions_to_set)
        else:
            self.hash = self.calculate_hash()
        super().save(*args, **kwargs)


def generate_wallet_address():
    random_id = str(uuid.uuid4())
    hash_object = hashlib.sha256(random_id.encode())
    wallet_address = hash_object.hexdigest()[:30]
    existing_wallet = Wallet.objects.filter(id=wallet_address)
    return wallet_address if not existing_wallet else generate_wallet_address()


class Wallet(models.Model):
    id = models.CharField(primary_key=True, max_length=30, default=generate_wallet_address, editable=False)
    issuer_id = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_linked = models.BooleanField(default=False)
    user_id = models.CharField(max_length=50, default="")
    

class PaperWallet(models.Model):
    creator_wallet = models.ForeignKey(Wallet, related_name='created_paper_wallets', on_delete=models.CASCADE)
    paper_wallet = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
