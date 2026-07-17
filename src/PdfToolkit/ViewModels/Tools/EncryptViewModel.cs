using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PdfSharp.Pdf;
using PdfSharp.Pdf.IO;
using PdfSharp.Pdf.Security;

namespace PdfToolkit.ViewModels.Tools;

public partial class EncryptViewModel : ViewModelBase
{
    private readonly MainWindowViewModel _mainVm;

    [ObservableProperty]
    private string _userPassword = string.Empty;

    [ObservableProperty]
    private string _ownerPassword = string.Empty;

    [ObservableProperty]
    private string _decryptPassword = string.Empty;

    public EncryptViewModel(MainWindowViewModel mainVm)
    {
        _mainVm = mainVm;
    }

    [RelayCommand]
    private async Task EncryptAsync()
    {
        if (string.IsNullOrWhiteSpace(UserPassword) && string.IsNullOrWhiteSpace(OwnerPassword))
        {
            _mainVm.StatusText = "Please enter at least one password";
            return;
        }

        string? sourcePath = null;

        if (_mainVm.DocumentModel.IsOpen)
        {
            sourcePath = _mainVm.DocumentModel.FilePath;
        }
        else
        {
            sourcePath = await _mainVm.FileDialogService.OpenPdfAsync(GetWindow());
        }

        if (sourcePath == null)
        {
            _mainVm.StatusText = "No PDF file selected";
            return;
        }

        var savePath = await _mainVm.FileDialogService.SavePdfAsync(GetWindow(), "encrypted.pdf");
        if (savePath == null) return;

        try
        {
            using var doc = PdfReader.Open(sourcePath, PdfDocumentOpenMode.Modify);

            if (!string.IsNullOrWhiteSpace(OwnerPassword))
                doc.SecuritySettings.OwnerPassword = OwnerPassword;
            if (!string.IsNullOrWhiteSpace(UserPassword))
                doc.SecuritySettings.UserPassword = UserPassword;

            doc.SecurityHandler.SetEncryptionToV2With128Bits();
            doc.SecuritySettings.PermitPrint = true;
            doc.SecuritySettings.PermitExtractContent = true;
            doc.SecuritySettings.PermitModifyDocument = true;
            doc.SecuritySettings.PermitAnnotations = true;
            doc.SecuritySettings.PermitAssembleDocument = true;
            doc.SecuritySettings.PermitFormsFill = true;

            doc.Save(savePath);
            _mainVm.StatusText = $"Encrypted and saved to {Path.GetFileName(savePath)}";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Encrypt failed: {ex.Message}";
        }
    }

    [RelayCommand]
    private async Task DecryptAsync()
    {
        if (string.IsNullOrWhiteSpace(DecryptPassword))
        {
            _mainVm.StatusText = "Please enter the decryption password";
            return;
        }

        string? sourcePath = null;

        if (_mainVm.DocumentModel.IsOpen)
        {
            sourcePath = _mainVm.DocumentModel.FilePath;
        }
        else
        {
            sourcePath = await _mainVm.FileDialogService.OpenPdfAsync(GetWindow());
        }

        if (sourcePath == null)
        {
            _mainVm.StatusText = "No PDF file selected";
            return;
        }

        var savePath = await _mainVm.FileDialogService.SavePdfAsync(GetWindow(), "decrypted.pdf");
        if (savePath == null) return;

        try
        {
            using var doc = PdfReader.Open(sourcePath, DecryptPassword, PdfDocumentOpenMode.Import);

            using var newDoc = new PdfDocument();
            foreach (var page in doc.Pages)
                newDoc.AddPage(page);

            newDoc.Save(savePath);
            _mainVm.StatusText = $"Decrypted and saved to {Path.GetFileName(savePath)}";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Decrypt failed: {ex.Message}";
        }
    }
}
