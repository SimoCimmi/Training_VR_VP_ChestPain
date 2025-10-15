using UnityEngine;
using System.IO;

public static class SavWav
{
    const int HEADER_SIZE = 44;

    public static bool Save(string filename, AudioClip clip)
    {
        if (!filename.ToLower().EndsWith(".wav"))
            filename += ".wav";

        var filepath = Path.Combine(Application.persistentDataPath, filename);

        Directory.CreateDirectory(Path.GetDirectoryName(filepath));
        using (var fileStream = CreateEmpty(filepath))
        {
            ConvertAndWrite(fileStream, clip);
            WriteHeader(fileStream, clip);
        }

        Debug.Log($" File WAV salvato in: {filepath}");
        return true;
    }

    static FileStream CreateEmpty(string filepath)
    {
        var fileStream = new FileStream(filepath, FileMode.Create);
        byte emptyByte = new byte();
        for (int i = 0; i < HEADER_SIZE; i++)
            fileStream.WriteByte(emptyByte);
        return fileStream;
    }

    static void ConvertAndWrite(FileStream fileStream, AudioClip clip)
    {
        float[] samples = new float[clip.samples];
        clip.GetData(samples, 0);
        short[] intData = new short[samples.Length];
        byte[] bytesData = new byte[samples.Length * 2];

        const float rescaleFactor = 32767f;

        for (int i = 0; i < samples.Length; i++)
        {
            intData[i] = (short)(samples[i] * rescaleFactor);
            byte[] byteArr = System.BitConverter.GetBytes(intData[i]);
            byteArr.CopyTo(bytesData, i * 2);
        }

        fileStream.Write(bytesData, 0, bytesData.Length);
    }

    static void WriteHeader(FileStream fileStream, AudioClip clip)
    {
        var hz = clip.frequency;
        var channels = clip.channels;
        var samples = clip.samples;

        fileStream.Seek(0, SeekOrigin.Begin);

        fileStream.Write(System.Text.Encoding.UTF8.GetBytes("RIFF"), 0, 4);
        fileStream.Write(System.BitConverter.GetBytes(fileStream.Length - 8), 0, 4);
        fileStream.Write(System.Text.Encoding.UTF8.GetBytes("WAVE"), 0, 4);
        fileStream.Write(System.Text.Encoding.UTF8.GetBytes("fmt "), 0, 4);
        fileStream.Write(System.BitConverter.GetBytes(16), 0, 4);
        fileStream.Write(System.BitConverter.GetBytes((ushort)1), 0, 2);
        fileStream.Write(System.BitConverter.GetBytes((ushort)channels), 0, 2);
        fileStream.Write(System.BitConverter.GetBytes(hz), 0, 4);
        fileStream.Write(System.BitConverter.GetBytes(hz * channels * 2), 0, 4);
        fileStream.Write(System.BitConverter.GetBytes((ushort)(channels * 2)), 0, 2);
        fileStream.Write(System.BitConverter.GetBytes((ushort)16), 0, 2);
        fileStream.Write(System.Text.Encoding.UTF8.GetBytes("data"), 0, 4);
        fileStream.Write(System.BitConverter.GetBytes(samples * channels * 2), 0, 4);
    }
}
