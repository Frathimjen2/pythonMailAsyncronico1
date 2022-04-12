def peastoneB(request):
    successful_submit = check_newsletter_submission(request)
    if request.method == "POSTIAR":
        send_email_task.delay(
            'Informacion sobre peastoneB',
            'Hello there!',
            'info @ xn - -Fratimjen - kic.pa',
            [request.POST['email']]
                        )
        successful_submit = True
    return render(request, "Fratimjen/peastoneB.html",
                  {"mail_mandado": successful_submit})