def modify_psd(model_class, account, old, new):
    if account.psd == old:
        model_class.objects.filter(pk=account.num).update(psd=new)
        return True
    else:
        return False
